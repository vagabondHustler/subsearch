import winreg

from subsearch.runtime.config import COMPUTER_NAME, REGISTRY_PATHS
from subsearch.runtime.recorder import LogLevel, capture


def read_registry_value(sub_key: str, value_name: str) -> str | None:
    try:
        with winreg.ConnectRegistry(COMPUTER_NAME, winreg.HKEY_CURRENT_USER) as hkey:
            with winreg.OpenKey(hkey, sub_key, 0, winreg.KEY_READ) as sk:
                value, _ = winreg.QueryValueEx(sk, value_name)
                return str(value)
    except FileNotFoundError:
        return None


def context_menu_key_exists() -> bool:
    try:
        with winreg.ConnectRegistry(COMPUTER_NAME, winreg.HKEY_CURRENT_USER) as hkey:
            with winreg.OpenKey(hkey, REGISTRY_PATHS.subsearch, 0, winreg.KEY_READ):
                return True
    except FileNotFoundError:
        return False


def del_registry_key(reg_path: str, key: str) -> None:
    capture(f"Deleting registry key: {key}", level=LogLevel.DEBUG)
    try:
        with winreg.ConnectRegistry(COMPUTER_NAME, winreg.HKEY_CURRENT_USER) as hkey:
            with winreg.OpenKey(hkey, reg_path, 0, winreg.KEY_WRITE) as sk:
                winreg.DeleteKey(sk, key)
    except FileNotFoundError:
        pass


def del_context_menu() -> None:
    capture("Removing Subsearch context menu from registry")
    del_registry_key(REGISTRY_PATHS.subsearch, "command")
    del_registry_key(REGISTRY_PATHS.shell, "Subsearch")


def create_context_menu_keys() -> None:
    registry_keys = [
        (REGISTRY_PATHS.classes, "*"),
        (REGISTRY_PATHS.asterisk, "shell"),
        (REGISTRY_PATHS.shell, "Subsearch"),
        (REGISTRY_PATHS.subsearch, "command"),
    ]
    with winreg.ConnectRegistry(COMPUTER_NAME, winreg.HKEY_CURRENT_USER) as hkey:
        for key, sub_key in registry_keys:
            capture(f"Attempting registry create key: {key}\\{sub_key}", level=LogLevel.DEBUG)
            with winreg.OpenKey(hkey, key, 0, winreg.KEY_WRITE) as sk:
                winreg.CreateKey(sk, sub_key)


def write_registry_value(sub_key: str, value_name: str, value: str) -> None:
    capture(f"Attempting registry set value: {sub_key}\\{value_name}", level=LogLevel.DEBUG)
    try:
        with winreg.ConnectRegistry(COMPUTER_NAME, winreg.HKEY_CURRENT_USER) as hkey:
            with winreg.OpenKey(hkey, sub_key, 0, winreg.KEY_WRITE) as sk:
                winreg.SetValueEx(sk, value_name, 0, winreg.REG_SZ, value)
    except FileNotFoundError:
        capture(f"Registry key missing, could not write {sub_key}\\{value_name}", level=LogLevel.WARNING)


def check_long_paths_enabled() -> bool:
    value_name = "LongPathsEnabled"
    try:
        with winreg.ConnectRegistry(COMPUTER_NAME, winreg.HKEY_LOCAL_MACHINE) as hkey:
            with winreg.OpenKey(hkey, REGISTRY_PATHS.long_paths, 0, winreg.KEY_READ) as sk:
                value, _ = winreg.QueryValueEx(sk, value_name)
                enabled = bool(value)
                if not enabled:
                    capture("Win32 long paths are not enabled, long file names may fail", level=LogLevel.WARNING)
                return enabled
    except FileNotFoundError:
        capture("Win32 long paths registry key not found, assuming disabled", level=LogLevel.WARNING)
        return False
    except Exception as check_error:
        capture(f"Failed to check long path status: {check_error}", level=LogLevel.ERROR)
        return False
