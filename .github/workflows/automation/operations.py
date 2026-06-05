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
ICON = "src/subsearch/gui/resources/assets/subsearch.ico"


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
    def set_output(self, name: str, value: str) -> None:
        with open(os.environ["GITHUB_OUTPUT"], "a") as github_output:
            print(f"{name}={value}", file=github_output)

    def add_summary(self, text: str) -> None:
        markdown = str(text).replace("%25", "%").replace("%0D", "\r").replace("%0A", "\n")
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a") as github_step_summary:
            github_step_summary.write(f"{markdown}\n")


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
        return f"VirusTotal analysis: [{file_name}]({VIRUSTOTAL_FILE_URL}/{file_hash})"

    def compare_link(self, previous_tag: str, current_tag: str) -> str:
        return f"Full changelog: [{current_tag}]({REPOSITORY_URL}/compare/{previous_tag}...{current_tag})"

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

        self._step_summary.add_summary(msi_analysis)
        self._step_summary.add_summary(exe_analysis)

        footer = f"###### {msi_analysis}<p>{exe_analysis}<p>{changelog_comparison}"
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


class Binaries:
    # Per stage, the expected state of (exe, log, config, registry key).
    _EXPECTED_STATE = {
        "install": (True, False, False, True),
        "executable": (True, True, True, True),
        "uninstall": (False, True, True, False),
    }
    _CHECK, _CROSS = ":heavy_check_mark:", ":x:"

    def __init__(self, step_summary: StepSummary) -> None:
        self._step_summary = step_summary

    def msi_artifact_path(self) -> Path:
        candidates = sorted(ARTIFACTS_PATH.glob("*.msi"))
        if not candidates:
            raise FileNotFoundError(f"No .msi found in {ARTIFACTS_PATH}")
        return candidates[0]

    # --- binary self-tests (run after the msi is built and downloaded) ------

    def test_msi_package(self, name: str, msi_package_path: Path) -> None:
        from subsearch.runtime.version import __version__

        installer_action = {"install": "/i", "uninstall": "/x"}[name]
        print(f"MSI Package is {name}ing Subsearch {__version__}")
        subprocess.run(["msiexec.exe", installer_action, str(msi_package_path), "/norestart", "/quiet"], check=True)
        print(f"{name.capitalize()} completed")

    def list_files_in_directory(self, directory: Path) -> None:
        try:
            for file in directory.glob("*"):
                print(file.as_posix())
        except OSError as error:
            print(f"Could not list {directory}: {error}")

    def is_process_running(self, process_name: str) -> bool:
        import psutil

        return any(
            (process.info["name"] or "").lower() == process_name.lower()
            for process in psutil.process_iter(["pid", "name"])
        )

    def wait_for_process(self, process_name: str, test_length: int) -> int:
        for duration in range(test_length + 1):
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

    def _print_file_content(self, file_path: Path) -> None:
        try:
            print(file_path.read_text())
        except OSError as error:
            print(f"Could not read {file_path}: {error}")

    def expected_files_exists(self) -> None:
        for path in (LOG_LOG_PATH, CONFIG_TOML_PATH):
            if not path.parent.exists():
                self.list_files_in_directory(path.parent.parent)
                raise FileNotFoundError(f"Directory '{path.parent}' does not exist.")
            if not path.is_file():
                self.list_files_in_directory(path.parent)
                raise FileNotFoundError(f"File '{path}' does not exist.")
            self._print_file_content(path)

    def test_executable(self, test_length: int = 30) -> None:
        process_name = EXE_INSTALLED_PATH.name
        print(f"{process_name} has been initiated for testing")
        subprocess.Popen([EXE_INSTALLED_PATH.as_posix()])
        print(f"Waiting {test_length} seconds for process...")
        duration = self.wait_for_process(process_name, test_length)
        self.expected_files_exists()
        print(f"{process_name} created expected files")
        print(f"{process_name} ran for the expected {test_length} seconds")
        if duration < test_length:
            raise RuntimeError(f"{process_name} did not run for the expected duration")
        self.end_process(process_name)

    def registry_key_exists(self) -> bool:
        import winreg  # Windows-only; imported lazily so this module loads on the Linux CI runner.

        try:
            with winreg.ConnectRegistry(socket.gethostname(), winreg.HKEY_CURRENT_USER) as hkey:
                winreg.OpenKey(hkey, r"Software\Classes\*\shell\Subsearch", 0, winreg.KEY_WRITE)
                return True
        except FileNotFoundError:
            return False

    # --- markdown step summary for the test results -------------------------

    def _current_state(self) -> tuple[bool, bool, bool, bool]:
        return EXE_INSTALLED_PATH.is_file(), LOG_LOG_PATH.is_file(), CONFIG_TOML_PATH.is_file(), self.registry_key_exists()

    def _emoji(self, flag: bool) -> str:
        return self._CHECK if flag else self._CROSS

    def _emoji_row(self, state: tuple[bool, bool, bool, bool]) -> str:
        return ", ".join(self._emoji(flag) for flag in state)

    def create_markdown_table_header(self) -> None:
        self._step_summary.add_summary(
            "| Test Stage | Exe exists | Log exists | Config exists | Registry key exists | Test result | Expected result |"
        )
        self._step_summary.add_summary("|---|---|---|---|---|---|---|")

    def add_markdown_table_result(self, name: str) -> None:
        state = self._current_state()
        expected = self._EXPECTED_STATE[name]
        passed = state == expected
        result = "Test passed" if passed else "Test failed"
        exe, log, cfg, key = (self._emoji(flag) for flag in state)

        self._step_summary.add_summary(
            f"| {name.capitalize()} test | {exe} | {log} | {cfg} | {key} | {result} | {self._emoji_row(expected)} |"
        )
        print("")
        print(f"Exe: {state[0]}, Log: {state[1]}, Config: {state[2]}, Registry key: {state[3]}")
        print(f"{name.capitalize()} {result}")
        print(STYLE_SEPARATOR)

        if not passed:
            self.list_files_in_directory(EXE_INSTALLED_PATH.parent)
            self.list_files_in_directory(LOG_LOG_PATH.parent)
            raise RuntimeError(f"{name} test failed")

    # --- hashing / artifact collection (run in the build job) ---------------

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
        self._step_summary.add_summary("| File | SHA256 |")
        self._step_summary.add_summary("|------|--------|")

        lines = []
        for file_path in (msi_freeze_path(), EXE_FREEZE_PATH):
            sha256 = self.calculate_sha256(file_path)
            suffix = file_path.suffix[1:]
            print(f"Setting new Github Action output: {suffix}_hash={sha256}")
            self._step_summary.set_output(f"{suffix}_hash", sha256)
            self._step_summary.add_summary(f"| {file_path.name} | {sha256} |")
            lines.append(f"{sha256} *{file_path.name}\n")

        print(f"Writing to {HASHES_PATH.name}")
        with open(HASHES_PATH, "w") as file:
            file.writelines(lines)


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
                base="Win32GUI",
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
