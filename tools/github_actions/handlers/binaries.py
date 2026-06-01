import hashlib
import socket
import subprocess
import time
import winreg
from pathlib import Path

import psutil

from subsearch.data.version import __version__
from tools.github_actions.globals import (
    ARTIFACTS_PATH,
    CONFIG_TOML_PATH,
    EXE_FREEZE_PATH,
    EXE_INSTALLED_PATH,
    HASHES_PATH,
    LOG_LOG_PATH,
    STYLE_SEPARATOR,
    msi_freeze_path,
)
from tools.github_actions.handlers import github_actions, log


def msi_artifact_path() -> Path:
    """Return the msi that prepare_build_artifacts moved into ./artifacts."""
    candidates = sorted(ARTIFACTS_PATH.glob("*.msi"))
    if not candidates:
        raise FileNotFoundError(f"No .msi found in {ARTIFACTS_PATH}")
    return candidates[0]


# --- binary self-tests (run after the msi is built and downloaded) ----------


def test_msi_package(name: str, msi_package_path: Path) -> None:
    installer_action = {"install": "/i", "uninstall": "/x"}[name]
    log.verbose_print(f"MSI Package is {name}ing Subsearch {__version__}")
    subprocess.run(["msiexec.exe", installer_action, str(msi_package_path), "/norestart", "/quiet"], check=True)
    log.verbose_print(f"{name.capitalize()} completed")


def list_files_in_directory(directory: Path) -> None:
    try:
        for file in directory.glob("*"):
            log.verbose_print(file.as_posix())
    except OSError as e:
        log.verbose_print(f"Could not list {directory}: {e}")


def is_process_running(process_name: str) -> bool:
    return any(p.info["name"].lower() == process_name.lower() for p in psutil.process_iter(["pid", "name"]))


def wait_for_process(process_name: str, test_length: int) -> int:
    for duration in range(test_length + 1):
        if not is_process_running(process_name):
            return duration
        time.sleep(1)
    return test_length


def end_process(process_name: str) -> None:
    for process in psutil.process_iter(["pid", "name"]):
        if process.info["name"].lower() == process_name.lower():
            log.verbose_print(f"Terminating {process_name}")
            process.terminate()


def _print_file_content(file_path: Path) -> None:
    try:
        print(file_path.read_text())
    except OSError as e:
        print(f"Could not read {file_path}: {e}")


def expected_files_exists() -> None:
    for path in (LOG_LOG_PATH, CONFIG_TOML_PATH):
        if not path.parent.exists():
            list_files_in_directory(path.parent.parent)
            raise FileNotFoundError(f"Directory '{path.parent}' does not exist.")
        if not path.is_file():
            list_files_in_directory(path.parent)
            raise FileNotFoundError(f"File '{path}' does not exist.")
        _print_file_content(path)


def test_executable(test_length: int = 30) -> None:
    process_name = EXE_INSTALLED_PATH.name
    log.verbose_print(f"{process_name} has been initiated for testing")
    subprocess.Popen([EXE_INSTALLED_PATH.as_posix()])
    log.verbose_print(f"Waiting {test_length} seconds for process...")
    duration = wait_for_process(process_name, test_length)
    expected_files_exists()
    log.verbose_print(f"{process_name} created expected files")
    log.verbose_print(f"{process_name} ran for the expected {test_length} seconds")
    if duration < test_length:
        raise RuntimeError(f"{process_name} did not run for the expected duration")
    end_process(process_name)


def registry_key_exists() -> bool:
    try:
        with winreg.ConnectRegistry(socket.gethostname(), winreg.HKEY_CURRENT_USER) as hkey:
            winreg.OpenKey(hkey, r"Software\Classes\*\shell\Subsearch", 0, winreg.KEY_WRITE)
            return True
    except FileNotFoundError:
        return False


# --- markdown step summary for the test results -----------------------------

# Per stage, the expected state of (exe, log, config, registry key).
_EXPECTED_STATE = {
    "install": (True, False, False, True),
    "executable": (True, True, True, True),
    "uninstall": (False, True, True, False),
}
_CHECK, _CROSS = ":heavy_check_mark:", ":x:"


def _current_state() -> tuple[bool, bool, bool, bool]:
    return EXE_INSTALLED_PATH.is_file(), LOG_LOG_PATH.is_file(), CONFIG_TOML_PATH.is_file(), registry_key_exists()


def _emoji(flag: bool) -> str:
    return _CHECK if flag else _CROSS


def _emoji_row(state: tuple[bool, bool, bool, bool]) -> str:
    return ", ".join(_emoji(flag) for flag in state)


def create_markdown_table_header() -> None:
    github_actions.set_step_summary(
        "| Test Stage | Exe exists | Log exists | Config exists | Registry key exists | Test result | Expected result |"
    )
    github_actions.set_step_summary("|---|---|---|---|---|---|---|")


def add_markdown_table_result(name: str) -> None:
    state = _current_state()
    expected = _EXPECTED_STATE[name]
    passed = state == expected
    result = "Test passed" if passed else "Test failed"
    exe, log_, cfg, key = (_emoji(f) for f in state)

    github_actions.set_step_summary(
        f"| {name.capitalize()} test | {exe} | {log_} | {cfg} | {key} | {result} | {_emoji_row(expected)} |"
    )
    print("")
    log.verbose_print(f"Exe: {state[0]}, Log: {state[1]}, Config: {state[2]}, Registry key: {state[3]}")
    log.verbose_print(f"{name.capitalize()} {result}")
    print(STYLE_SEPARATOR)

    if not passed:
        list_files_in_directory(EXE_INSTALLED_PATH.parent)
        list_files_in_directory(LOG_LOG_PATH.parent)
        raise RuntimeError(f"{name} test failed")


# --- hashing / artifact collection (run in the build job) -------------------


def calculate_sha256(file_path: Path) -> str:
    if not file_path.is_file():
        raise FileNotFoundError(f"No file found at {file_path}")
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as file:
        for byte_block in iter(lambda: file.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def prepare_build_artifacts() -> None:
    log.verbose_print("Collecting files")
    ARTIFACTS_PATH.mkdir(parents=True, exist_ok=True)
    for file in (msi_freeze_path(), EXE_FREEZE_PATH):
        file.replace(ARTIFACTS_PATH / file.name)
        log.verbose_print(f"{file.name} moved to ./artifacts")


def write_to_hashes() -> None:
    """Hash the freshly built binaries, write hashes.sha256, and emit a
    `<suffix>_hash=<value>` step output plus a step-summary table for each."""
    log.verbose_print("Collecting hashes")
    ARTIFACTS_PATH.mkdir(parents=True, exist_ok=True)
    github_actions.set_step_summary("| File | SHA256 |")
    github_actions.set_step_summary("|------|--------|")

    lines = []
    for file_path in (msi_freeze_path(), EXE_FREEZE_PATH):
        sha256 = calculate_sha256(file_path)
        suffix = file_path.suffix[1:]
        log.verbose_print(f"Setting new Github Action output: {suffix}_hash={sha256}")
        github_actions.set_step_output(f"{suffix}_hash", sha256)
        github_actions.set_step_summary(f"| {file_path.name} | {sha256} |")
        lines.append(f"{sha256} *{file_path.name}\n")

    log.verbose_print(f"Writing to {HASHES_PATH.name}")
    with open(HASHES_PATH, "w") as file:
        file.writelines(lines)
