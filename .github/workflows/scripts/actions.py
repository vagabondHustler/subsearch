import hashlib
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from config import (
    APP_NAME,
    APP_USER_MODEL_ID,
    CHANGELOG_NAME,
    EXE_NAME,
    REPOSITORY_URL,
    STYLE_SEPARATOR,
    VIRUSTOTAL_FILE_URL,
    Paths,
)

_OCTICON_PASSED = (
    '<svg viewBox="0 0 16 16" width="16" height="16" fill="#1a7f37" aria-hidden="true">'
    '<path d="M8 16A8 8 0 1 1 8 0a8 8 0 0 1 0 16Zm3.78-9.72a.751.751 0 0 0-.018-1.042.751.751 0 0 0-1.042-.018L6.75 9.19 '
    '5.28 7.72a.751.751 0 0 0-1.042.018.751.751 0 0 0-.018 1.042l2 2a.75.75 0 0 0 1.06 0Z"></path></svg>'
)
_OCTICON_FAILED = (
    '<svg viewBox="0 0 16 16" width="16" height="16" fill="#cf222e" aria-hidden="true">'
    '<path d="M2.343 13.657A8 8 0 1 1 13.658 2.343 8 8 0 0 1 2.343 13.657ZM6.03 4.97a.751.751 0 0 0-1.042.018.751.751 0 0 '
    "0-.018 1.042L6.94 8 4.97 9.97a.749.749 0 0 0 .326 1.275.749.749 0 0 0 .734-.215L8 9.06l1.97 1.97a.749.749 0 0 0 "
    '1.275-.326.749.749 0 0 0-.215-.734L9.06 8l1.97-1.97a.749.749 0 0 0-.326-1.275.749.749 0 0 0-.734.215L8 6.94Z"></path></svg>'
)


def octicon(passed: bool) -> str:
    return _OCTICON_PASSED if passed else _OCTICON_FAILED


def log(message: str, level: str = "INFO") -> None:
    timestamp = datetime.now(timezone.utc).strftime("%H:%M:%S.%f")[:-3]
    print(f"[{timestamp}] {level:<4} {message}", flush=True)


def msi_name(version: str) -> str:
    return f"Subsearch-{version}-win64.msi"


def artifact_id(version: str, ref_name: str, run_id: str) -> str:
    return f"{version}_{ref_name}_{run_id}"


def msi_freeze_path() -> Path:
    candidates = sorted(Paths.dist.glob("*.msi"))
    if not candidates:
        raise FileNotFoundError(f"No .msi found in {Paths.dist}")
    return candidates[0]


class StepSummary:
    PASSED, FAILED = "PASSED", "FAILED"

    def set_output(self, name: str, value: str) -> None:
        with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as github_output:
            print(f"{name}={value}", file=github_output)

    def add_summary(self, text: str) -> None:
        markdown = str(text).replace("%25", "%").replace("%0D", "\r").replace("%0A", "\n")
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as github_step_summary:
            github_step_summary.write(f"{markdown}\n")

    def card(self, title: str, passed: bool | None = None) -> None:
        if passed is None:
            self.add_summary(f"### {title}")
            return
        glyph = octicon(passed)
        self.add_summary(f"### {glyph} {title} {self.PASSED if passed else self.FAILED}")

    def fields(self, items: list[tuple[str, str]]) -> None:
        for label, value in items:
            self.add_summary(f"- **{label}:** {value}")

    def result(self, condition: bool) -> str:
        return self.PASSED if condition else self.FAILED


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
        result = subprocess.run([*self._COMMAND, "version", "--project"], check=True, capture_output=True, text=True)
        return result.stdout.strip()

    def bump_version(self) -> None:
        # cz bump exits non-zero with NoneIncrementError when no commits warrant a
        # release; the caller detects that no-op by comparing versions, so the
        # failure is swallowed here rather than treated as an error.
        subprocess.run([*self._COMMAND, "bump", "--yes"])

    def predicted_next_version(self) -> str | None:
        result = subprocess.run([*self._COMMAND, "bump", "--dry-run", "--yes"], capture_output=True, text=True)
        if result.returncode != 0:
            return None
        for line in result.stdout.splitlines():
            if line.strip().startswith(self._TAG_TO_CREATE_PREFIX):
                return line.split(self._TAG_TO_CREATE_PREFIX, 1)[1].strip()
        return None

    def render_changelog_for_tag(self, tag: str, file_name: Path) -> None:
        completed = subprocess.run([*self._COMMAND, "changelog", tag, "--file-name", str(file_name)])
        if completed.returncode != 0:
            self.render_unreleased_changelog(tag, file_name)

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
        msi_virustotal_link = self.virustotal_link(msi_name, msi_hash)
        exe_virustotal_link = self.virustotal_link(exe_name, exe_hash)
        comparison_link = self.compare_link(previous_tag, current_tag)

        self._step_summary.card(f"Release {current_tag}")
        self._step_summary.fields(
            [
                ("MSI", msi_virustotal_link),
                ("Exe", exe_virustotal_link),
                ("Changelog", comparison_link),
            ]
        )

        footer = (
            f"###### VirusTotal: {msi_virustotal_link}<p>VirusTotal: {exe_virustotal_link}"
            f"<p>Full changelog: {comparison_link}"
        )
        with open(Paths.artifacts / CHANGELOG_NAME, "a") as changelog_file:
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
    log(f"Listing contents of {directory.as_posix()}")
    try:
        for file in directory.glob("*"):
            log(f"  {file.as_posix()}")
    except OSError as error:
        log(f"Could not list {directory}: {error}", level="FAIL")


def registry_key_exists() -> bool:
    import winreg  # Windows-only; imported lazily so this module loads on the Linux CI runner.

    try:
        winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Classes\*\shell\Subsearch", 0, winreg.KEY_READ)
        return True
    except FileNotFoundError:
        return False


def read_registry_value(sub_key: str, value_name: str) -> str | None:
    import winreg  # Windows-only; imported lazily so this module loads on the Linux CI runner.

    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, sub_key, 0, winreg.KEY_READ) as key:
            value, _ = winreg.QueryValueEx(key, value_name)
            return str(value)
    except FileNotFoundError:
        return None


# (label, sub_key, value_name) for the context-menu entries the app populates on first launch.
REGISTRY_VALUE_PROBES = (
    ("Subsearch", r"Software\Classes\*\shell\Subsearch", ""),
    ("Icon", r"Software\Classes\*\shell\Subsearch", "Icon"),
    ("AppliesTo", r"Software\Classes\*\shell\Subsearch", "AppliesTo"),
    ("command", r"Software\Classes\*\shell\Subsearch\command", ""),
)


def read_registry_values() -> list[tuple[str, str | None]]:
    return [(label, read_registry_value(sub_key, value_name)) for label, sub_key, value_name in REGISTRY_VALUE_PROBES]


class BinaryTester:
    def msi_artifact_path(self) -> Path:
        candidates = sorted(Paths.artifacts.glob("*.msi"))
        if not candidates:
            raise FileNotFoundError(f"No .msi found in {Paths.artifacts}")
        return candidates[0]

    def _version_from_msi(self, msi_package_path: Path) -> str:
        match = re.search(r"Subsearch-(.+)-win64\.msi", msi_package_path.name)
        return match.group(1) if match else "unknown"

    def test_msi_package(self, name: str, msi_package_path: Path) -> None:
        installer_action = {"install": "/i", "uninstall": "/x"}[name]
        log(f"MSI package is {name}ing Subsearch {self._version_from_msi(msi_package_path)}", level="STEP")
        subprocess.run(["msiexec.exe", installer_action, str(msi_package_path), "/norestart", "/quiet"], check=True)
        log(f"{name.capitalize()} completed", level="PASS")

    def is_process_running(self, process_name: str) -> bool:
        import psutil

        return any(
            (process.info["name"] or "").lower() == process_name.lower()
            for process in psutil.process_iter(["pid", "name"])
        )

    def wait_for_process_start(self, process: "subprocess.Popen", process_name: str, timeout: int = 5) -> None:
        log(f"Waiting up to {timeout}s for {process_name} to start", level="STEP")
        for elapsed in range(timeout):
            if process.poll() is not None:
                raise RuntimeError(f"{process_name} exited during startup with code {process.returncode}")
            if self.is_process_running(process_name):
                log(f"{process_name} started after {elapsed}s", level="PASS")
                return
            time.sleep(1)
        raise RuntimeError(f"{process_name} did not start within {timeout} seconds")

    def wait_for_process(self, process: "subprocess.Popen", process_name: str, test_length: int) -> int:
        import psutil

        log(f"Watching {process_name} for up to {test_length}s", level="STEP")
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
                log(f"{process_name} no longer visible by name after {duration}s", level="STEP")
                return duration
            time.sleep(1)
        log(f"{process_name} still running after {test_length}s", level="PASS")
        return test_length

    def end_process(self, process_name: str) -> None:
        import psutil

        for process in psutil.process_iter(["pid", "name"]):
            if (process.info["name"] or "").lower() == process_name.lower():
                log(f"Terminating {process_name}", level="STEP")
                process.terminate()
                try:
                    returncode = process.wait(timeout=10)
                    log(f"{process_name} terminated with code {returncode}", level="PASS")
                except psutil.TimeoutExpired:
                    log(f"{process_name} did not terminate within 10s; killing", level="FAIL")
                    process.kill()

    def visible_window_owned_by(self, pids: set[int]) -> bool:
        import win32gui
        import win32process

        found = False

        def visit(handle: int, _) -> bool:
            nonlocal found
            if not win32gui.IsWindowVisible(handle):
                return True
            _, owner_pid = win32process.GetWindowThreadProcessId(handle)
            if owner_pid in pids:
                found = True
            return True

        win32gui.EnumWindows(visit, None)
        return found

    def process_tree_pids(self, process_name: str) -> set[int]:
        import psutil

        pids: set[int] = set()
        for process in psutil.process_iter(["pid", "name"]):
            if (process.info["name"] or "").lower() == process_name.lower():
                pids.add(process.info["pid"])
        return pids

    def assert_window_rendered(self, process_name: str = EXE_NAME, timeout: int = 60) -> None:
        log(f"Waiting up to {timeout}s for a visible window owned by {process_name}", level="STEP")
        for elapsed in range(timeout):
            if self.visible_window_owned_by(self.process_tree_pids(process_name)):
                log(f"Visible GUI window for '{process_name}' present after {elapsed}s", level="PASS")
                return
            time.sleep(1)
        raise RuntimeError(f"No visible GUI window for '{process_name}' appeared within {timeout} seconds")

    def _print_file_content(self, file_path: Path) -> None:
        log(f"Contents of {file_path.as_posix()}")
        try:
            print(file_path.read_text(encoding="utf-8", errors="replace"))
        except OSError as error:
            log(f"Could not read {file_path}: {error}", level="FAIL")

    def wait_for_file(self, path: Path, timeout: int) -> None:
        log(f"Waiting up to {timeout}s for {path.as_posix()}", level="STEP")
        for elapsed in range(timeout):
            if path.is_file():
                log(f"{path.name} appeared after {elapsed}s", level="PASS")
                return
            time.sleep(1)
        if not path.parent.exists():
            list_files_in_directory(path.parent.parent)
            raise FileNotFoundError(f"Directory '{path.parent}' does not exist.")
        list_files_in_directory(path.parent)
        raise FileNotFoundError(f"File '{path}' did not appear within {timeout} seconds.")

    def expected_files_exists(self, timeout: int = 30) -> None:
        for path in (Paths.log_file, Paths.config_file):
            self.wait_for_file(path, timeout)
            self._print_file_content(path)

    def assert_log_is_clean(self) -> None:
        log_text = Paths.log_file.read_text(encoding="utf-8", errors="replace")
        offending = [line for line in log_text.splitlines() if "ERROR" in line or "CRITICAL" in line]
        if offending:
            raise RuntimeError("Log contains ERROR/CRITICAL entries:\n" + "\n".join(offending))

    def _launch_executable(self) -> "subprocess.Popen":
        log(f"{EXE_NAME} has been initiated for testing", level="STEP")
        return subprocess.Popen([Paths.installed_executable.as_posix()])

    def _verify_startup(self, process: "subprocess.Popen", test_length: int) -> int:
        self.wait_for_process_start(process, EXE_NAME)
        self.assert_window_rendered()
        return self.wait_for_process(process, EXE_NAME, test_length)

    def _verify_runtime_artifacts(self, test_length: int) -> None:
        self.expected_files_exists(test_length)
        self.assert_log_is_clean()
        log(f"{EXE_NAME} created expected files", level="PASS")

    def _verify_run_duration(self, duration: int, test_length: int) -> None:
        if duration < test_length:
            raise RuntimeError(f"{EXE_NAME} did not run for the expected duration")
        log(f"{EXE_NAME} ran for the expected {test_length}s", level="PASS")

    def test_executable(self, test_length: int = 30) -> None:
        process = self._launch_executable()
        duration = self._verify_startup(process, test_length)
        self._verify_runtime_artifacts(test_length)
        self._verify_run_duration(duration, test_length)
        self.end_process(EXE_NAME)


class Check:
    def __init__(self, label: str, expected: bool, actual: bool, detail: str) -> None:
        self.label = label
        self.expected = expected
        self.actual = actual
        self.detail = detail

    @property
    def passed(self) -> bool:
        return self.actual == self.expected


class BinaryTestReport:
    _TITLES = {
        "install": "MSI install",
        "executable": "Subsearch ran",
        "uninstall": "MSI uninstall",
    }

    def __init__(self, step_summary: StepSummary) -> None:
        self._step_summary = step_summary

    def _path_check(self, label: str, path: Path, expected: bool) -> Check:
        present = path.is_file()
        detail = path.as_posix() if present else f"missing ({path.as_posix()})"
        return Check(label, expected, present, detail)

    def _registry_value_checks(self, expected_populated: bool) -> list[Check]:
        checks = []
        for label, value in read_registry_values():
            populated = value not in (None, "")
            if value is None:
                detail = "key absent"
            elif value == "":
                detail = "empty placeholder"
            else:
                detail = f"`{value}`"
            checks.append(Check(f"Registry {label}", expected_populated, populated, detail))
        return checks

    def _checks_for_install(self) -> list[Check]:
        return [
            self._path_check("Executable", Paths.installed_executable, expected=True),
            self._path_check("Start Menu shortcut", Paths.start_menu_shortcut, expected=True),
            *self._registry_value_checks(expected_populated=False),
        ]

    def _checks_for_executable(self) -> list[Check]:
        return [
            self._path_check("Executable", Paths.installed_executable, expected=True),
            self._path_check("Log", Paths.log_file, expected=True),
            self._path_check("Config", Paths.config_file, expected=True),
            *self._registry_value_checks(expected_populated=True),
        ]

    def _checks_for_uninstall(self) -> list[Check]:
        return [
            self._path_check("Executable removed", Paths.installed_executable, expected=False),
            self._path_check("Start Menu shortcut removed", Paths.start_menu_shortcut, expected=False),
            Check("Registry key removed", expected=False, actual=registry_key_exists(), detail="HKCU context-menu key"),
        ]

    def _checks_for_stage(self, name: str) -> list[Check]:
        return {
            "install": self._checks_for_install,
            "executable": self._checks_for_executable,
            "uninstall": self._checks_for_uninstall,
        }[name]()

    def add_stage_card(self, name: str) -> None:
        checks = self._checks_for_stage(name)
        passed = all(check.passed for check in checks)
        self._step_summary.card(f"{self._TITLES[name]}: {self._step_summary.result(passed)}", passed=passed)
        self._step_summary.add_summary("Reason:")
        for check in checks:
            mark = self._step_summary.result(check.passed)
            self._step_summary.add_summary(f"- {check.label}: {mark} - {check.detail}")
        self._log_stage(name, checks, passed)
        self._assert_stage_passed(name, passed)

    def _assert_stage_passed(self, name: str, passed: bool) -> None:
        if not passed:
            list_files_in_directory(Paths.installed_executable.parent)
            list_files_in_directory(Paths.log_file.parent)
            raise RuntimeError(f"{name} test failed")

    def _log_stage(self, name: str, checks: list[Check], passed: bool) -> None:
        for check in checks:
            log(f"{check.label}: {'OK' if check.passed else 'BAD'} ({check.detail})")
        log(f"{self._TITLES[name]} {'passed' if passed else 'failed'}", level="PASS" if passed else "FAIL")
        print(STYLE_SEPARATOR)


class ArtifactHasher:
    def __init__(self, step_summary: StepSummary) -> None:
        self._step_summary = step_summary

    def calculate_sha256(self, file_path: Path) -> str:
        if not file_path.is_file():
            raise FileNotFoundError(f"No file found at {file_path}")
        hasher = hashlib.sha256()
        with open(file_path, "rb") as file:
            for chunk in iter(lambda: file.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    def _collect_artifact_paths(self) -> tuple[Path, Path]:
        return msi_freeze_path(), Paths.frozen_executable

    def _compute_hashes(self, paths: tuple[Path, Path]) -> dict[Path, str]:
        return {path: self.calculate_sha256(path) for path in paths}

    def _publish_hash_outputs(self, hashes: dict[Path, str]) -> None:
        for file_path, sha256 in hashes.items():
            output_name = f"{file_path.suffix[1:]}_hash"
            log(f"Setting new GitHub Action output: {output_name}={sha256}")
            self._step_summary.set_output(output_name, sha256)

    def _write_hashes_file(self, hashes: dict[Path, str]) -> None:
        log(f"Writing to {Paths.hashes.name}")
        with open(Paths.hashes, "w") as hashes_file:
            hashes_file.writelines(f"{sha256} *{file_path.name}\n" for file_path, sha256 in hashes.items())

    def _write_hashes_summary(self, hashes: dict[Path, str]) -> None:
        self._step_summary.card("Build artifacts")
        for file_path, sha256 in hashes.items():
            self._step_summary.add_summary(f"- {file_path.name}: `{sha256}`")

    def prepare_build_artifacts(self) -> None:
        log("Collecting files", level="STEP")
        Paths.artifacts.mkdir(parents=True, exist_ok=True)
        for file in self._collect_artifact_paths():
            file.replace(Paths.artifacts / file.name)
            log(f"{file.name} moved to ./artifacts")

    def write_to_hashes(self) -> None:
        log("Collecting hashes", level="STEP")
        Paths.artifacts.mkdir(parents=True, exist_ok=True)
        hashes = self._compute_hashes(self._collect_artifact_paths())
        self._publish_hash_outputs(hashes)
        self._write_hashes_summary(hashes)
        self._write_hashes_file(hashes)


class Build:
    _PACKAGES_TO_INCLUDE = [
        "curl_cffi",
        "imdbinfo",
        "num2words",
        "packaging",
        "PySide6",
        "qfluentwidgets",
        "requests",
        "selectolax",
        "yaspin",
        "termcolor",
        "urllib3",
        "urllib3_future",
        "qh3",
        "jh2",
        "wassima",
        "cryptography",
    ]

    _INCLUDES = [
        "selectolax.lexbor",
        "selectolax.parser",
    ]
    _PACKAGES_TO_EXCLUDE = [
        "tkinter",
        "unittest",
        "test",
        "pydoc_data",
        "lib2to3",
        "distutils",
        "setuptools",
        "pip",
        "xmlrpc",
        "sqlite3",
        "curses",
        "email",
        "html",
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
                icon=str(Paths.icon),
                shortcut_name="Subsearch",
                shortcut_dir="ProgramMenuFolder",
            )
        ]

    def _selectolax_namespace_packages(self) -> list[tuple[str, str]]:
        # selectolax's modest namespace package has no __init__.py, so cx_Freeze drops it; copy it back in.
        import selectolax

        selectolax_root = Path(selectolax.__file__).parent
        return [(str(selectolax_root / "modest"), "lib/selectolax/modest")]

    def _bdist_msi_options(self) -> dict:
        from subsearch.runtime.config.guid import __guid__

        return {
            "upgrade_code": f"{__guid__}",
            "install_icon": str(Paths.icon),
            "data": self._data_table(),
            "launch_on_finish": True,
        }

    def _build_exe_options(self) -> dict:
        license_files = [("LICENSE", "LICENSE"), ("THIRD-PARTY-LICENSES.md", "THIRD-PARTY-LICENSES.md")]
        return {
            "include_files": license_files + self._selectolax_namespace_packages(),
            "includes": self._INCLUDES,
            "packages": self._PACKAGES_TO_INCLUDE,
            "excludes": self._PACKAGES_TO_EXCLUDE,
        }

    def _options(self) -> dict:
        return {"build_exe": self._build_exe_options(), "bdist_msi": self._bdist_msi_options()}

    def _log_build_start(self) -> None:
        log(f"Freezing {APP_NAME} into an exe and packaging it as a Windows msi", level="STEP")
        log(f"Including {len(self._PACKAGES_TO_INCLUDE)} packages, excluding {len(self._PACKAGES_TO_EXCLUDE)}")

    def _run_cx_freeze(self) -> None:
        from cx_Freeze import setup

        sys.argv = [sys.argv[0], "bdist_msi"]
        setup(options=self._options(), executables=self._executables())

    def _log_build_result(self) -> None:
        log(f"Created exe at {Paths.frozen_executable.as_posix()}", level="PASS")
        log(f"Created msi at {msi_freeze_path().as_posix()}", level="PASS")
        print(STYLE_SEPARATOR)

    def _set_shortcut_app_user_model_id(self) -> None:
        import warnings

        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", "'msilib' is deprecated")
            import msilib

        msi_path = msi_freeze_path()
        database = msilib.OpenDatabase(str(msi_path), msilib.MSIDBOPEN_TRANSACT)
        # MsiShortcutProperty is a standard MSI table but is absent from msilib.schema, so the
        # build never creates it; create it before inserting the AUMID that links toasts to the
        # Start Menu shortcut (cx_Freeze names the first executable's shortcut row "S_APP_0").
        database.OpenView(
            "CREATE TABLE `MsiShortcutProperty` ("
            "`MsiShortcutProperty` CHAR(72) NOT NULL, "
            "`Shortcut_` CHAR(72) NOT NULL, "
            "`PropertyKey` CHAR(72) NOT NULL, "
            "`PropVariantValue` CHAR(255) NOT NULL "
            "PRIMARY KEY `MsiShortcutProperty`)"
        ).Execute(None)
        msilib.add_data(
            database,
            "MsiShortcutProperty",
            [("AppUserModelID", "S_APP_0", "System.AppUserModel.ID", APP_USER_MODEL_ID)],
        )
        database.Commit()
        log(f"Set shortcut AppUserModelID to {APP_USER_MODEL_ID}", level="PASS")

    def make_msi(self) -> None:
        self._log_build_start()
        self._run_cx_freeze()
        self._set_shortcut_app_user_model_id()
        self._log_build_result()


class ReleaseValidation:
    SOURCE_TREE = "src/subsearch"
    MARKER = "release-validation"
    RESULT_PASSED = "passed"
    RESULT_FAILED = "failed"

    # Matches the marker HTML comment: <!-- release-validation:result=passed;src=<hash>;run=<id> -->
    _STATE_PATTERN = re.compile(
        r"<!--\s*release-validation:result=(?P<result>\w+);src=(?P<src>[0-9a-f]+);run=(?P<run>\d+)\s*-->"
    )

    def open_release_pr(self) -> str | None:
        completed = subprocess.run(
            [
                "gh",
                "pr",
                "list",
                "--base",
                "main",
                "--head",
                "dev",
                "--state",
                "open",
                "--draft",
                "--label",
                "release",
                "--json",
                "number",
                "--jq",
                ".[0].number",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        number = completed.stdout.strip()
        return number or None

    def src_tree_hash(self, commit: str = "HEAD") -> str:
        completed = subprocess.run(
            ["git", "rev-parse", f"{commit}:{self.SOURCE_TREE}"],
            check=True,
            capture_output=True,
            text=True,
        )
        return completed.stdout.strip()

    def pr_head_sha(self, number: str) -> str:
        completed = subprocess.run(
            ["gh", "pr", "view", number, "--json", "headRefOid", "--jq", ".headRefOid"],
            check=True,
            capture_output=True,
            text=True,
        )
        return completed.stdout.strip()

    def last_validation(self, number: str) -> tuple[str, str, str] | None:
        completed = subprocess.run(
            ["gh", "pr", "view", number, "--json", "comments", "--jq", ".comments[].body"],
            check=True,
            capture_output=True,
            text=True,
        )
        match = None
        for line in completed.stdout.splitlines():
            found = self._STATE_PATTERN.search(line)
            if found:
                match = found
        if match is None:
            return None
        return match.group("src"), match.group("result"), match.group("run")

    def should_validate(self, number: str) -> bool:
        previous = self.last_validation(number)
        if previous is None:
            return True
        validated_src, result, _ = previous
        if result != self.RESULT_PASSED:
            return True
        return validated_src != self.src_tree_hash(self.pr_head_sha(number))

    def _marker_body(self, src_tree_hash: str, result: str, run_id: str) -> str:
        comment = f"<!-- {self.MARKER}:result={result};src={src_tree_hash};run={run_id} -->"
        passed = result == self.RESULT_PASSED
        status = "Release validation passed" if passed else "Release validation failed"
        return f"{comment}\n{octicon(passed)} **{status}** — src tree `{src_tree_hash}` (run {run_id})"

    def _has_marker_comment(self, number: str) -> bool:
        completed = subprocess.run(
            ["gh", "pr", "view", number, "--json", "comments"],
            check=True,
            capture_output=True,
            text=True,
        )
        comments = json.loads(completed.stdout)["comments"]
        return any(f"<!-- {self.MARKER}:" in comment["body"] for comment in comments)

    def record_validation(self, number: str, src_tree_hash: str, result: str, run_id: str) -> None:
        body = self._marker_body(src_tree_hash, result, run_id)
        command = ["gh", "pr", "comment", number, "--body", body]
        if self._has_marker_comment(number):
            command.append("--edit-last")
        subprocess.run(command, check=True)
