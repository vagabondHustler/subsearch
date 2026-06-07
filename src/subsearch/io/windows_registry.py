import sys
import winreg
from pathlib import Path

from subsearch.runtime.logging.logger import log
from subsearch.runtime.config.constants import (
    APP_PATHS,
    COMPUTER_NAME,
    DEVICE_INFO,
    FILE_PATHS,
    REGISTRY_PATHS,
)
from subsearch.io import toml_file
from subsearch.io.toml_file import diagnostics_enabled


class PythonExecutable:
    def __init__(self, show_terminal: bool) -> None:
        python_dir = Path(sys.executable).parent
        self.path = python_dir / ("python.exe" if show_terminal else "pythonw.exe")


class RegistryLaunchCommand:
    def __init__(self) -> None:
        show_terminal = toml_file.load_toml_value(FILE_PATHS.config, "application.show_terminal")
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
    show_icon: str = toml_file.load_toml_value(FILE_PATHS.config, "shell_integration.context_menu_icon")
    if show_icon:
        return str(APP_PATHS.ui_assets / "subsearch.ico")
    else:
        return ""


def get_appliesto_value() -> str:
    file_extensions = toml_file.load_toml_value(FILE_PATHS.config, "shell_integration.file_extensions")
    enabled_extensions = [f'".{ext}"' for ext, enabled in file_extensions.items() if enabled]
    return " OR ".join(enabled_extensions)


def del_registry_key(reg_path: str, key: str) -> None:
    if diagnostics_enabled():
        log.debug(f"Deleting registry key: {reg_path}\\{key}")
    with winreg.ConnectRegistry(COMPUTER_NAME, winreg.HKEY_CURRENT_USER) as hkey:
        with winreg.OpenKey(hkey, reg_path, 0, winreg.KEY_WRITE) as sk:
            winreg.DeleteKey(sk, key)


def del_context_menu() -> None:
    log.info("Removing Subsearch context menu from registry")
    del_registry_key(REGISTRY_PATHS.subsearch, "command")
    del_registry_key(REGISTRY_PATHS.shell, "Subsearch")


def write_keys() -> None:
    registry_keys = [
        (REGISTRY_PATHS.classes, "*"),
        (REGISTRY_PATHS.asterisk, "shell"),
        (REGISTRY_PATHS.shell, "Subsearch"),
        (REGISTRY_PATHS.subsearch, "command"),
    ]
    with winreg.ConnectRegistry(COMPUTER_NAME, winreg.HKEY_CURRENT_USER) as hkey:
        for key, sub_key in registry_keys:
            if diagnostics_enabled():
                log.debug(f"Creating registry key: {key}\\{sub_key}")
            with winreg.OpenKey(hkey, key, 0, winreg.KEY_WRITE) as sk:
                winreg.CreateKey(sk, sub_key)


def write_registry_value(sub_key: str, value_name: str, value: str) -> None:
    try:
        if diagnostics_enabled():
            log.debug(f"Setting registry value: {sub_key} [{value_name or '(default)'}] = {value!r}")
        with winreg.ConnectRegistry(COMPUTER_NAME, winreg.HKEY_CURRENT_USER) as hkey:
            with winreg.OpenKey(hkey, sub_key, 0, winreg.KEY_WRITE) as sk:
                winreg.SetValueEx(sk, value_name, 0, winreg.REG_SZ, value)
    except FileNotFoundError:
        pass


def write_registry_value_by_key(key: str) -> None:
    key_map = {
        "subsearch": {"key_type": REGISTRY_PATHS.subsearch, "value_name": "", "value": "Subsearch"},
        "icon": {"key_type": REGISTRY_PATHS.subsearch, "value_name": "Icon", "value": get_icon_value()},
        "appliesto": {"key_type": REGISTRY_PATHS.subsearch, "value_name": "AppliesTo", "value": get_appliesto_value()},
        "command": {"key_type": REGISTRY_PATHS.subsearch_command, "value_name": "", "value": get_command_value()},
    }

    key = key.lower()
    if key in key_map:
        key_type = key_map[key]["key_type"]
        value_name = key_map[key]["value_name"]
        value = key_map[key]["value"]
        write_registry_value(key_type, value_name, value)


def write_all_registry_values() -> None:
    items = ["subsearch", "icon", "appliesto", "command"]
    for item in items:
        write_registry_value_by_key(item)


def add_context_menu() -> None:
    log.info("Adding Subsearch context menu to registry")
    write_keys()
    write_all_registry_values()


def check_long_paths_enabled() -> bool:
    value_name = "LongPathsEnabled"

    try:
        with winreg.ConnectRegistry(COMPUTER_NAME, winreg.HKEY_LOCAL_MACHINE) as hkey:
            with winreg.OpenKey(hkey, REGISTRY_PATHS.long_paths, 0, winreg.KEY_READ) as sk:
                value, _ = winreg.QueryValueEx(sk, value_name)
                enabled = bool(value)
                if not enabled:
                    log.warning("Win32 long paths are not enabled — long file names may fail")
                return enabled
    except FileNotFoundError:
        log.warning("Win32 long paths registry key not found — assuming disabled")
        return False
    except Exception as e:
        log.error(f"Failed to check long path status: {e}")
        return False
