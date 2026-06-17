import sys
import winreg
from collections.abc import Mapping
from pathlib import Path

from subsearch.runtime.config import (
    APP_PATHS,
    COMPUTER_NAME,
    DEVICE_INFO,
    REGISTRY_PATHS,
)
from subsearch.runtime.config import session as config_session
from subsearch.runtime.config.defaults import ConfigKey
from subsearch.runtime.logging.events import LogEvent
from subsearch.runtime.logging.logger import log


class PythonExecutable:
    def __init__(self, show_terminal: bool) -> None:
        python_dir = Path(sys.executable).parent
        self.path = python_dir / ("python.exe" if show_terminal else "pythonw.exe")


class RegistryLaunchCommand:
    def __init__(self) -> None:
        show_terminal = config_session.read_config_value(ConfigKey.APPLICATION_SHOW_TERMINAL)
        self._mode = DEVICE_INFO.mode
        self._python_executable = PythonExecutable(show_terminal)

    def _executable_mode_command(self) -> str:
        return f'"{sys.argv[0]}" "%1"'

    def _interpreter_mode_command(self) -> str:
        console_title = "import ctypes; ctypes.windll.kernel32.SetConsoleTitleW('subsearch');"
        working_directory = f"import os; os.chdir(r'{APP_PATHS.home}');"
        import_subsearch = "import subsearch; subsearch.main()"
        return f'{self._python_executable.path} -c "{console_title} {working_directory} {import_subsearch}" "%1"'

    def build(self) -> str:
        if self._mode == "executable":
            return self._executable_mode_command()
        return self._interpreter_mode_command()


def get_command_value() -> str:
    return RegistryLaunchCommand().build()


def get_icon_value() -> str:
    show_icon: str = config_session.read_config_value(ConfigKey.SHELL_INTEGRATION_CONTEXT_MENU_ICON)
    if show_icon:
        return str(APP_PATHS.ui_assets / "subsearch.ico")
    else:
        return ""


def get_appliesto_value() -> str:
    file_extensions = config_session.read_config_value(ConfigKey.SHELL_INTEGRATION_FILE_EXTENSIONS)
    enabled_extensions = [f'".{ext}"' for ext, enabled in file_extensions.items() if enabled]
    return " OR ".join(enabled_extensions)


VALUE_LOCATIONS = {
    "subsearch": (REGISTRY_PATHS.subsearch, ""),
    "icon": (REGISTRY_PATHS.subsearch, "Icon"),
    "appliesto": (REGISTRY_PATHS.subsearch, "AppliesTo"),
    "command": (REGISTRY_PATHS.subsearch_command, ""),
}


def desired_registry_values() -> dict[str, str]:
    return {
        "subsearch": "Subsearch",
        "icon": get_icon_value(),
        "appliesto": get_appliesto_value(),
        "command": get_command_value(),
    }


def changed_value_names(desired: Mapping[str, str], current: Mapping[str, str | None]) -> list[str]:
    return [name for name, value in desired.items() if current.get(name) != value]


def _read_registry_value(sub_key: str, value_name: str) -> str | None:
    try:
        with winreg.ConnectRegistry(COMPUTER_NAME, winreg.HKEY_CURRENT_USER) as hkey:
            with winreg.OpenKey(hkey, sub_key, 0, winreg.KEY_READ) as sk:
                value, _ = winreg.QueryValueEx(sk, value_name)
                return str(value)
    except FileNotFoundError:
        return None


def current_registry_values() -> dict[str, str | None]:
    return {name: _read_registry_value(sub_key, value_name) for name, (sub_key, value_name) in VALUE_LOCATIONS.items()}


def _context_menu_key_exists() -> bool:
    try:
        with winreg.ConnectRegistry(COMPUTER_NAME, winreg.HKEY_CURRENT_USER) as hkey:
            with winreg.OpenKey(hkey, REGISTRY_PATHS.subsearch, 0, winreg.KEY_READ):
                return True
    except FileNotFoundError:
        return False


def _del_registry_key(reg_path: str, key: str) -> None:
    log.event(LogEvent.REGISTRY_KEY_DELETING, level="debug", key=key)
    try:
        with winreg.ConnectRegistry(COMPUTER_NAME, winreg.HKEY_CURRENT_USER) as hkey:
            with winreg.OpenKey(hkey, reg_path, 0, winreg.KEY_WRITE) as sk:
                winreg.DeleteKey(sk, key)
    except FileNotFoundError:
        pass


def _del_context_menu() -> None:
    log.event(LogEvent.REGISTRY_CONTEXT_MENU_REMOVING)
    _del_registry_key(REGISTRY_PATHS.subsearch, "command")
    _del_registry_key(REGISTRY_PATHS.shell, "Subsearch")


def _create_context_menu_keys() -> None:
    registry_keys = [
        (REGISTRY_PATHS.classes, "*"),
        (REGISTRY_PATHS.asterisk, "shell"),
        (REGISTRY_PATHS.shell, "Subsearch"),
        (REGISTRY_PATHS.subsearch, "command"),
    ]
    with winreg.ConnectRegistry(COMPUTER_NAME, winreg.HKEY_CURRENT_USER) as hkey:
        for key, sub_key in registry_keys:
            log.event(LogEvent.REGISTRY_ATTEMPTING, level="debug", action="create key", target=f"{key}\\{sub_key}")
            with winreg.OpenKey(hkey, key, 0, winreg.KEY_WRITE) as sk:
                winreg.CreateKey(sk, sub_key)


def _write_registry_value(sub_key: str, value_name: str, value: str) -> None:
    log.event(LogEvent.REGISTRY_ATTEMPTING, level="debug", action="set value", target=f"{sub_key}\\{value_name}")
    try:
        with winreg.ConnectRegistry(COMPUTER_NAME, winreg.HKEY_CURRENT_USER) as hkey:
            with winreg.OpenKey(hkey, sub_key, 0, winreg.KEY_WRITE) as sk:
                winreg.SetValueEx(sk, value_name, 0, winreg.REG_SZ, value)
    except FileNotFoundError:
        log.event(LogEvent.REGISTRY_KEY_MISSING, level="warning", sub_key=sub_key, value_name=value_name)


def reconcile_shell_integration() -> None:
    if DEVICE_INFO.mode == "executable":
        log.event(LogEvent.REGISTRY_RECONCILE_SKIPPED, level="debug")
        return
    context_menu_enabled = config_session.read_config_value(ConfigKey.SHELL_INTEGRATION_CONTEXT_MENU)
    if not context_menu_enabled:
        if _context_menu_key_exists():
            _del_context_menu()
        else:
            log.event(LogEvent.REGISTRY_MATCHES_ABSENT, level="debug")
        return
    desired = desired_registry_values()
    stale_names = changed_value_names(desired, current_registry_values())
    if not stale_names:
        log.event(LogEvent.REGISTRY_MATCHES_CURRENT, level="debug")
        return
    _create_context_menu_keys()
    for name in stale_names:
        sub_key, value_name = VALUE_LOCATIONS[name]
        _write_registry_value(sub_key, value_name, desired[name])
        log.event(LogEvent.REGISTRY_VALUE_UPDATED, name=name)


def check_long_paths_enabled() -> bool:
    value_name = "LongPathsEnabled"

    try:
        with winreg.ConnectRegistry(COMPUTER_NAME, winreg.HKEY_LOCAL_MACHINE) as hkey:
            with winreg.OpenKey(hkey, REGISTRY_PATHS.long_paths, 0, winreg.KEY_READ) as sk:
                value, _ = winreg.QueryValueEx(sk, value_name)
                enabled = bool(value)
                if not enabled:
                    log.event(LogEvent.REGISTRY_LONG_PATHS_DISABLED, level="warning")
                return enabled
    except FileNotFoundError:
        log.event(LogEvent.REGISTRY_LONG_PATHS_KEY_MISSING, level="warning")
        return False
    except Exception as e:
        log.event(LogEvent.REGISTRY_LONG_PATHS_CHECK_FAILED, level="error", reason=str(e))
        return False
