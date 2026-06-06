"""Reusable operations for the release/maintenance workflows.

Run by file path (`python .github/workflows/automation/workflows.py <name>`) rather
than as a `-m` module, because `.github` cannot be a Python package. Anything that
needs the repo root on sys.path relies on the workflow's working directory being the
checkout root, which GitHub Actions guarantees.
"""

import hashlib
import os
import re
import socket
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPOSITORY_URL = "https://github.com/vagabondHustler/subsearch"
VIRUSTOTAL_FILE_URL = "https://www.virustotal.com/gui/file"

STYLE_SEPARATOR = "-" * 120

EXE_NAME = "Subsearch.exe"
HASHES_NAME = "hashes.sha256"
CHANGELOG_NAME = "changelog.md"

HOME_PATH = Path.home()
EXE_INSTALLED_PATH = HOME_PATH / "AppData" / "Local" / "Programs" / "Subsearch" / EXE_NAME
LOG_LOG_PATH = HOME_PATH / "AppData" / "Local" / "Subsearch" / "log.log"
CONFIG_TOML_PATH = HOME_PATH / "AppData" / "Local" / "Subsearch" / "config.toml"

CWD_PATH = Path.cwd()
ARTIFACTS_PATH = CWD_PATH / "artifacts"
DIST_PATH = CWD_PATH / "dist"
EXE_FREEZE_PATH = CWD_PATH / "build" / f"exe.win-amd64-{sys.version_info[0]}.{sys.version_info[1]}" / EXE_NAME
HASHES_PATH = ARTIFACTS_PATH / HASHES_NAME


APP_NAME = "Subsearch"
ICON = str(CWD_PATH / "src" / "subsearch" / "ui" / "assets" / "subsearch.ico")


def msi_name(version: str) -> str:
    return f"Subsearch-{version}-win64.msi"


def artifact_id(version: str, ref_name: str, run_id: str) -> str:
    return f"{version}_{ref_name}_{run_id}"


def msi_freeze_path() -> Path:
    candidates = sorted(DIST_PATH.glob("*.msi"))
    if not candidates:
        raise FileNotFoundError(f"No .msi found in {DIST_PATH}")
    return candidates[0]


class StepSummary:
    """Append GitHub Actions step-summary cards: titled sections with a status,
    rendered as markdown that GitHub displays at the top of each job."""

    CHECK, CROSS = ":heavy_check_mark:", ":x:"

    def set_output(self, name: str, value: str) -> None:
        with open(os.environ["GITHUB_OUTPUT"], "a") as github_output:
            print(f"{name}={value}", file=github_output)

    def add_summary(self, text: str) -> None:
        markdown = str(text).replace("%25", "%").replace("%0D", "\r").replace("%0A", "\n")
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a") as github_step_summary:
            github_step_summary.write(f"{markdown}\n")

    def card(self, title: str, passed: bool | None = None) -> None:
        badge = "" if passed is None else f" {self.CHECK if passed else self.CROSS}"
        self.add_summary(f"### {title}{badge}")

    def table(self, headers: tuple[str, ...], rows: list[tuple[str, ...]]) -> None:
        self.add_summary("| " + " | ".join(headers) + " |")
        self.add_summary("|" + "|".join(["---"] * len(headers)) + "|")
        for row in rows:
            self.add_summary("| " + " | ".join(row) + " |")

    def fields(self, items: list[tuple[str, str]]) -> None:
        for label, value in items:
            self.add_summary(f"- **{label}:** {value}")

    def emoji(self, flag: bool) -> str:
        return self.CHECK if flag else self.CROSS


class Git:
    def push_with_tags(self, branch: str) -> None:
        subprocess.run(["git", "push", "origin", f"HEAD:{branch}", "--follow-tags"], check=True)

    def commit_all(self, message: str) -> None:
        subprocess.run(["git", "add", "--all"], check=True)
        subprocess.run(["git", "commit", "--message", message], check=True)

    def push(self, branch: str) -> None:
        subprocess.run(["git", "push", "origin", f"HEAD:{branch}"], check=True)

    def fetch(self, branch: str, with_tags: bool = False) -> None:
        command = ["git", "fetch", "origin", branch]
        if with_tags:
            command.append("--tags")
        subprocess.run(command, check=True)

    def fast_forward_branch(self, source_branch: str, target_branch: str) -> None:
        self.fetch(source_branch, with_tags=True)
        subprocess.run(["git", "push", "origin", f"origin/{source_branch}:refs/heads/{target_branch}"], check=True)


class Commitizen:
    # Invoked as a module rather than the `cz` console script so the current working
    # directory is on sys.path and the SubsearchCz plugin (in tools/) is importable.
    _COMMAND = [sys.executable, "-m", "commitizen"]
    _TAG_TO_CREATE_PREFIX = "tag to create:"

    def current_version(self) -> str:
        completed = subprocess.run([*self._COMMAND, "version", "--project"], check=True, capture_output=True, text=True)
        return completed.stdout.strip()

    def bump_version(self) -> None:
        # cz bump exits non-zero with NoneIncrementError when no commits warrant a
        # release; the caller detects that no-op by comparing versions, so the
        # failure is swallowed here rather than treated as an error.
        subprocess.run([*self._COMMAND, "bump", "--yes"])

    def predicted_next_version(self) -> str | None:
        completed = subprocess.run([*self._COMMAND, "bump", "--dry-run", "--yes"], capture_output=True, text=True)
        if completed.returncode != 0:
            return None
        for line in completed.stdout.splitlines():
            if line.strip().startswith(self._TAG_TO_CREATE_PREFIX):
                return line.split(self._TAG_TO_CREATE_PREFIX, 1)[1].strip()
        return None

    def render_changelog_for_tag(self, tag: str, file_name: Path) -> None:
        subprocess.run([*self._COMMAND, "changelog", tag, "--file-name", str(file_name)], check=True)

    def render_unreleased_changelog(self, unreleased_version: str, file_name: Path) -> None:
        subprocess.run(
            [*self._COMMAND, "changelog", "--unreleased-version", unreleased_version, "--file-name", str(file_name)],
            check=True,
        )


class Changelog:
    def __init__(self, step_summary: StepSummary) -> None:
        self._step_summary = step_summary

    def virustotal_link(self, file_name: str, file_hash: str) -> str:
        return f"[{file_name}]({VIRUSTOTAL_FILE_URL}/{file_hash})"

    def compare_link(self, previous_tag: str, current_tag: str) -> str:
        return f"[{previous_tag}...{current_tag}]({REPOSITORY_URL}/compare/{previous_tag}...{current_tag})"

    def append_release_links(
        self,
        current_tag: str,
        previous_tag: str,
        msi_name: str,
        msi_hash: str,
        exe_name: str,
        exe_hash: str,
    ) -> None:
        msi_analysis = self.virustotal_link(msi_name, msi_hash)
        exe_analysis = self.virustotal_link(exe_name, exe_hash)
        changelog_comparison = self.compare_link(previous_tag, current_tag)

        self._step_summary.card(f"Release {current_tag}")
        self._step_summary.fields(
            [
                ("MSI", msi_analysis),
                ("Exe", exe_analysis),
                ("Changelog", changelog_comparison),
            ]
        )

        footer = (
            f"###### VirusTotal: {msi_analysis}<p>VirusTotal: {exe_analysis}"
            f"<p>Full changelog: {changelog_comparison}"
        )
        with open(ARTIFACTS_PATH / CHANGELOG_NAME, "a") as changelog_file:
            changelog_file.write(footer)


class LicenseYear:
    COPYRIGHT_PATTERN = re.compile(r"Copyright \(C\) (\d{4})(?:-\d{4})? vagabondHustler")

    def current_year(self) -> int:
        return datetime.now(timezone.utc).year

    def renew_copyright_year(self, license_text: str, year: int) -> str:
        def replace(match: re.Match[str]) -> str:
            start_year = int(match.group(1))
            span = f"{start_year}-{year}" if year > start_year else f"{start_year}"
            return f"Copyright (C) {span} vagabondHustler"

        return self.COPYRIGHT_PATTERN.sub(replace, license_text, count=1)

    def update_license_file(self, license_path: Path, year: int) -> bool:
        original = license_path.read_text(encoding="utf-8")
        renewed = self.renew_copyright_year(original, year)
        if renewed == original:
            return False
        license_path.write_text(renewed, encoding="utf-8", newline="\n")
        return True


def list_files_in_directory(directory: Path) -> None:
    try:
        for file in directory.glob("*"):
            print(file.as_posix())
    except OSError as error:
        print(f"Could not list {directory}: {error}")


def registry_key_exists() -> bool:
    import winreg  # Windows-only; imported lazily so this module loads on the Linux CI runner.

    try:
        with winreg.ConnectRegistry(socket.gethostname(), winreg.HKEY_CURRENT_USER) as hkey:
            winreg.OpenKey(hkey, r"Software\Classes\*\shell\Subsearch", 0, winreg.KEY_WRITE)
            return True
    except FileNotFoundError:
        return False


class BinaryTester:
    """Install, run, and uninstall the built binary to prove it works end to end."""

    def msi_artifact_path(self) -> Path:
        candidates = sorted(ARTIFACTS_PATH.glob("*.msi"))
        if not candidates:
            raise FileNotFoundError(f"No .msi found in {ARTIFACTS_PATH}")
        return candidates[0]

    def test_msi_package(self, name: str, msi_package_path: Path) -> None:
        from subsearch.runtime.version import __version__

        installer_action = {"install": "/i", "uninstall": "/x"}[name]
        print(f"MSI Package is {name}ing Subsearch {__version__}")
        subprocess.run(["msiexec.exe", installer_action, str(msi_package_path), "/norestart", "/quiet"], check=True)
        print(f"{name.capitalize()} completed")

    def is_process_running(self, process_name: str) -> bool:
        import psutil

        return any(
            (process.info["name"] or "").lower() == process_name.lower()
            for process in psutil.process_iter(["pid", "name"])
        )

    def wait_for_process_start(self, process: "subprocess.Popen", process_name: str, timeout: int = 5) -> None:
        for _ in range(timeout):
            if process.poll() is not None:
                raise RuntimeError(f"{process_name} exited during startup with code {process.returncode}")
            if self.is_process_running(process_name):
                return
            time.sleep(1)
        raise RuntimeError(f"{process_name} did not start within {timeout} seconds")

    def wait_for_process(self, process: "subprocess.Popen", process_name: str, test_length: int) -> int:
        import psutil

        for duration in range(test_length + 1):
            returncode = process.poll()
            if returncode is not None:
                raise RuntimeError(f"{process_name} exited early after {duration}s with code {returncode}")
            try:
                if psutil.Process(process.pid).status() in (psutil.STATUS_ZOMBIE, psutil.STATUS_DEAD):
                    raise RuntimeError(f"{process_name} became defunct after {duration}s")
            except psutil.NoSuchProcess:
                raise RuntimeError(f"{process_name} vanished after {duration}s")
            if not self.is_process_running(process_name):
                return duration
            time.sleep(1)
        return test_length

    def end_process(self, process_name: str) -> None:
        import psutil

        for process in psutil.process_iter(["pid", "name"]):
            if (process.info["name"] or "").lower() == process_name.lower():
                print(f"Terminating {process_name}")
                process.terminate()
                try:
                    returncode = process.wait(timeout=10)
                    print(f"{process_name} terminated with code {returncode}")
                except psutil.TimeoutExpired:
                    print(f"{process_name} did not terminate within 10s; killing")
                    process.kill()

    def window_exists(self, window_title: str) -> bool:
        import win32gui

        return win32gui.FindWindow(None, window_title) != 0

    def assert_window_rendered(self, window_title: str = APP_NAME, timeout: int = 5) -> None:
        for _ in range(timeout):
            if self.window_exists(window_title):
                print(f"GUI window '{window_title}' is present")
                return
            time.sleep(1)
        raise RuntimeError(f"GUI window '{window_title}' did not appear within {timeout} seconds")

    def _print_file_content(self, file_path: Path) -> None:
        try:
            print(file_path.read_text())
        except OSError as error:
            print(f"Could not read {file_path}: {error}")

    def expected_files_exists(self) -> None:
        for path in (LOG_LOG_PATH, CONFIG_TOML_PATH):
            if not path.parent.exists():
                list_files_in_directory(path.parent.parent)
                raise FileNotFoundError(f"Directory '{path.parent}' does not exist.")
            if not path.is_file():
                list_files_in_directory(path.parent)
                raise FileNotFoundError(f"File '{path}' does not exist.")
            self._print_file_content(path)

    def assert_log_is_clean(self) -> None:
        log_text = LOG_LOG_PATH.read_text(encoding="utf-8", errors="replace")
        offending = [line for line in log_text.splitlines() if "ERROR" in line or "CRITICAL" in line]
        if offending:
            raise RuntimeError("Log contains ERROR/CRITICAL entries:\n" + "\n".join(offending))

    def test_executable(self, test_length: int = 30) -> None:
        process_name = EXE_INSTALLED_PATH.name
        print(f"{process_name} has been initiated for testing")
        process = subprocess.Popen([EXE_INSTALLED_PATH.as_posix()])
        self.wait_for_process_start(process, process_name)
        self.assert_window_rendered()
        print(f"Waiting {test_length} seconds for process...")
        duration = self.wait_for_process(process, process_name, test_length)
        self.expected_files_exists()
        self.assert_log_is_clean()
        print(f"{process_name} created expected files")
        print(f"{process_name} ran for the expected {test_length} seconds")
        if duration < test_length:
            raise RuntimeError(f"{process_name} did not run for the expected duration")
        self.end_process(process_name)


class BinaryTestReport:
    """Render the per-stage install/run/uninstall results as a step-summary card per stage."""

    _PROBES = ("Exe", "Log", "Config", "Registry key")

    # Per stage, the expected presence of (exe, log, config, registry key).
    _EXPECTED_STATE = {
        "install": (True, False, False, True),
        "executable": (True, True, True, True),
        "uninstall": (False, True, True, False),
    }

    def __init__(self, step_summary: StepSummary) -> None:
        self._step_summary = step_summary

    def _current_state(self) -> tuple[bool, bool, bool, bool]:
        return EXE_INSTALLED_PATH.is_file(), LOG_LOG_PATH.is_file(), CONFIG_TOML_PATH.is_file(), registry_key_exists()

    def add_stage_card(self, name: str) -> None:
        actual = self._current_state()
        expected = self._EXPECTED_STATE[name]
        passed = actual == expected

        rows = [
            (probe, self._step_summary.emoji(is_present), self._step_summary.emoji(should_exist))
            for probe, is_present, should_exist in zip(self._PROBES, actual, expected)
        ]
        self._step_summary.card(f"{name.capitalize()} test", passed=passed)
        self._step_summary.table(("Probe", "Found", "Expected"), rows)

        self._log_stage(name, actual, passed)
        if not passed:
            list_files_in_directory(EXE_INSTALLED_PATH.parent)
            list_files_in_directory(LOG_LOG_PATH.parent)
            raise RuntimeError(f"{name} test failed")

    def _log_stage(self, name: str, actual: tuple[bool, bool, bool, bool], passed: bool) -> None:
        print("")
        print(", ".join(f"{probe}: {present}" for probe, present in zip(self._PROBES, actual)))
        print(f"{name.capitalize()} test {'passed' if passed else 'failed'}")
        print(STYLE_SEPARATOR)


class ArtifactHasher:
    """Collect the frozen msi/exe into ./artifacts and record their sha256 hashes."""

    def __init__(self, step_summary: StepSummary) -> None:
        self._step_summary = step_summary

    def calculate_sha256(self, file_path: Path) -> str:
        if not file_path.is_file():
            raise FileNotFoundError(f"No file found at {file_path}")
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as file:
            for byte_block in iter(lambda: file.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def prepare_build_artifacts(self) -> None:
        print("Collecting files")
        ARTIFACTS_PATH.mkdir(parents=True, exist_ok=True)
        for file in (msi_freeze_path(), EXE_FREEZE_PATH):
            file.replace(ARTIFACTS_PATH / file.name)
            print(f"{file.name} moved to ./artifacts")

    def write_to_hashes(self) -> None:
        print("Collecting hashes")
        ARTIFACTS_PATH.mkdir(parents=True, exist_ok=True)

        hashes = {file_path: self.calculate_sha256(file_path) for file_path in (msi_freeze_path(), EXE_FREEZE_PATH)}

        for file_path, sha256 in hashes.items():
            output_name = f"{file_path.suffix[1:]}_hash"
            print(f"Setting new Github Action output: {output_name}={sha256}")
            self._step_summary.set_output(output_name, sha256)

        self._step_summary.card("Build artifacts")
        self._step_summary.table(
            ("File", "SHA256"),
            [(file_path.name, f"`{sha256}`") for file_path, sha256 in hashes.items()],
        )

        print(f"Writing to {HASHES_PATH.name}")
        with open(HASHES_PATH, "w") as file:
            file.writelines(f"{sha256} *{file_path.name}\n" for file_path, sha256 in hashes.items())


class Build:
    """Freeze the app into an exe and package it as a Windows msi via cx_Freeze."""

    _LIBS_TO_EXCLUDE = [
        "concurrent",
        "lib2to3",
        "multiprocessing",
        "distutils",
        "tcl8",
        "test",
        "unittest",
        "xml",
        "xmlrpc",
        "asyncio",
        "chardet",
    ]

    def _data_table(self) -> dict:
        script_component = f"_cx_executable0__Executable_script_src_{APP_NAME.lower()}___main__.py_"
        registry_path = r"Software\Classes\*\shell\Subsearch"
        return {
            "Registry": {
                (f"{APP_NAME}_key", -1, registry_path, None, None, script_component),
                (f"{APP_NAME}_regz_icon", -1, registry_path, "Icon", None, script_component),
                (f"{APP_NAME}_regz_appliesto", -1, registry_path, "AppliesTo", None, script_component),
                (f"{APP_NAME}_key_command", -1, rf"{registry_path}\command", None, "", script_component),
            },
        }

    def _executables(self) -> list:
        from cx_Freeze import Executable

        return [
            Executable(
                "src/subsearch/__main__.py",
                base="gui",
                target_name=APP_NAME,
                icon=ICON,
                shortcut_name="Subsearch",
                shortcut_dir="ProgramMenuFolder",
            )
        ]

    def _options(self) -> dict:
        from subsearch.runtime.guid import __guid__

        bdist_msi = {"upgrade_code": f"{__guid__}", "install_icon": ICON, "data": self._data_table()}
        license_files = [("LICENSE", "LICENSE"), ("THIRD-PARTY-LICENSES.md", "THIRD-PARTY-LICENSES.md")]
        build_exe = {"excludes": [*self._LIBS_TO_EXCLUDE], "include_files": license_files}
        return {"build_exe": build_exe, "bdist_msi": bdist_msi}

    def make_msi(self) -> None:
        # cx_Freeze's setup() reads the command from sys.argv, so set it explicitly
        # rather than depending on how this script was invoked.
        from cx_Freeze import setup

        sys.argv = [sys.argv[0], "bdist_msi"]
        setup(options=self._options(), executables=self._executables())
