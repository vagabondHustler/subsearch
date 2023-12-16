import hashlib
import socket
import subprocess
import time
import winreg
from pathlib import Path
from typing import Any

from tools.cli.globals import (
    APP_CONFIG_PATH,
    APP_LOG_PATH,
    ARTIFACTS_PATH,
    EXE_BUILD,
    EXE_INSTALLED,
    HASHES_PATH,
    MSI_DIST,
    PRE_RELEASE,
    STYLE_SEPERATOR,
)
from tools.cli.handlers import github_actions, io_json, io_python, log


def test_msi_package(name: str, msi_package_path: Path) -> None:
    _app_version = io_python.read_string()
    installer_action = {"install": "/i", "uninstall": "/x"}.get(name, None)
    log.verbose_print(f"MSI Package is {name}ing Subsearch {_app_version}")
    command = ["msiexec.exe", installer_action, msi_package_path, "/norestart", "/quiet"]
    subprocess.run(command, check=True)
    log.verbose_print(f"{name.capitalize()} completed")


def is_process_running(process_name) -> bool:
    try:
        result = subprocess.run(["tasklist", "/FI", f"IMAGENAME eq {process_name}"], capture_output=True, text=True)
        return process_name.lower() in result.stdout.lower()
    except subprocess.CalledProcessError:
        return False


def wait_for_process(process: subprocess.Popen[bytes], test_lenght: int) -> int:
    log.verbose_print(f"Subsearch.exe has been initiated for testing")
    duration = 0
    while process.poll() is None and duration <= test_lenght:
        time.sleep(1)
        if is_process_running("Subsearch.exe"):
            log.verbose_print(f"Subsearch.exe is running ({duration}/{test_lenght} seconds)")
            duration += 1
        else:
            log.verbose_print(f"Subsearch.exe unexpectedly terminated")
            break
    return duration


def end_process(process: subprocess.Popen[bytes]) -> None:
    if process.poll() is None:
        log.verbose_print(f"Terminating Subsearch.exe")
        process.kill()


def print_exe_duration(duration: int, test_lenght: int):
    if duration >= test_lenght:
        log.verbose_print(f"Subsearch.exe ran for 10 seconds without crashing")
    else:
        log.verbose_print(f"Subsearch.exe did not run for the expected duration")


def test_executable(test_lenght: int = 10) -> None:
    try:
        process = subprocess.Popen([EXE_INSTALLED.as_posix()])
        duration = wait_for_process(process, test_lenght)
        print_exe_duration(duration, test_lenght)
    except Exception as e:
        log.verbose_print(f"An unexpected error occurred during testing: {e}")
    finally:
        end_process(process)


def registry_key_exists() -> bool:
    try:
        with winreg.ConnectRegistry(socket.gethostname(), winreg.HKEY_CURRENT_USER) as hkey:
            winreg.OpenKey(hkey, r"Software\Classes\*\shell\Subsearch", 0, winreg.KEY_WRITE)
            return True
    except FileNotFoundError:
        return False


def _software_test_result(name: str, result: str) -> None:
    summary = f"EXE exists: {EXE_INSTALLED.is_file()}, LOG exists: {APP_LOG_PATH.is_file()}, CONFIG exists: {APP_CONFIG_PATH.is_file()}. REGISTY_KEY exists: {registry_key_exists()}"
    print(f"")
    log.verbose_print(f"{summary}")
    log.verbose_print(f"{name.capitalize()} {result}")
    print(f"{STYLE_SEPERATOR}")


def set_test_result(name: str) -> None:
    tests = {
        "install": EXE_INSTALLED.is_file() and registry_key_exists(),
        "executable": APP_LOG_PATH.is_file() and APP_CONFIG_PATH.is_file(),
        "uninstall": not EXE_INSTALLED.is_file() and not registry_key_exists(),
    }
    if tests[name]:
        _software_test_result(name, "passed")
    else:
        _software_test_result(name, "failed")
        raise RuntimeError(f"{name} test failed")


def calculate_sha256(file_path: str) -> str:
    sha256_hash = hashlib.sha256()
    file_path = Path(file_path)
    if not Path(file_path).is_file():
        raise FileNotFoundError(f"No file found at {file_path}")

    with open(file_path, "rb") as file:
        for byte_block in iter(lambda: file.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def create_hashes_file(**kwargs: dict[str, Any]) -> None:
    hashes_path = kwargs.get("hashes_path", HASHES_PATH)
    if not ARTIFACTS_PATH.is_dir():
        ARTIFACTS_PATH.mkdir(parents=True, exist_ok=True)
    with open(hashes_path, "w") as f:
        pass
    log.verbose_print(f"Created file: {hashes_path}")


def write_to_hashes(**kwargs: dict[str, Any]) -> None:
    lines: dict[int, str] = {}
    file_paths: list[Path] = kwargs.get("hashes_path", [MSI_DIST, EXE_BUILD])
    hashes_path: Path = kwargs.get("hashes_path", HASHES_PATH)

    if not hashes_path.is_file():
        create_hashes_file(hashes_path=hashes_path)

    for enum, file_path in enumerate(file_paths):
        sha256 = calculate_sha256(file_path)
        file_name = f"{file_path.name}"
        lines[enum] = f"{sha256} *{file_name}\n"
        github_actions.set_output(name=f"{file_name}_hash", value=f"{sha256}")

    with open(hashes_path, "a") as file:
        file.writelines(lines.values())

    [log.verbose_print(f"Wrote {i} to {hashes_path}") for i in lines.values()]
