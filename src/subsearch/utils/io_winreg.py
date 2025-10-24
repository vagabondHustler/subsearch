import sys
import winreg
from pathlib import Path

from subsearch.globals.constants import (
    APP_PATHS,
    FILE_PATHS,
    SYSTEM_INFO,
)
from subsearch.utils import io_toml


class LaunchOptions:
    def __init__(self) -> None:
        self.show_terminal: bool = io_toml.load_toml_value(FILE_PATHS.config, "gui.show_terminal")
        self.python_dir: Path = Path(sys.executable).parent
        self.console_title_stmt: str = "import ctypes; ctypes.windll.kernel32.SetConsoleTitleW('subsearch');"
        self.chdir_stmt: str = f"import os; os.chdir(r'{APP_PATHS.home}');"
        self.run_stmt: str = "import subsearch; subsearch.main()"

    def _python_binary(self) -> str:
        name = "python.exe" if self.show_terminal else "pythonw.exe"
        return str(self.python_dir / name)

    def _executable_command(self) -> str:
        return f'"{sys.argv[0]}" "%1"'

    def _interpreter_command(self) -> str:
        return f'{self._python_binary()} -c "{self.console_title_stmt} {self.chdir_stmt} {self.run_stmt}" "%1"'

    def build_command(self) -> str:
        if SYSTEM_INFO.mode == "executable":
            return self._executable_command()
        if SYSTEM_INFO.mode == "interpreter":
            return self._interpreter_command()
        return self._executable_command()

    def _get_mode_executable(self) -> str:
        return self._executable_command()

    def _get_mode_interpreter(self) -> str:
        return self._interpreter_command()

    def get_parameter(self) -> str:
        return self.build_command()


Hive = winreg.HKEYType


def _ensure_key(hive: Hive, key_path: str) -> winreg.HKEYType:
    try:
        return winreg.CreateKeyEx(hive, key_path, 0, access=winreg.KEY_READ | winreg.KEY_WRITE)
    except OSError:
        return winreg.CreateKeyEx(hive, key_path, 0, access=winreg.KEY_READ)


def _set_value(
    hive: Hive, key_path: str, value_name: str | None, value_data: str, value_type: int = winreg.REG_SZ
) -> None:
    key = _ensure_key(hive, key_path)
    winreg.SetValueEx(key, value_name, 0, value_type, value_data)
    winreg.CloseKey(key)


def _default_menu_text() -> str:
    return "Subsearch"


def _default_icon_path() -> str:
    return str(Path(sys.executable))


def _default_command() -> str:
    return f'"{sys.executable}" -m subsearch "%1"'


def _context_menu_paths() -> tuple[Hive, str, str]:
    hive = winreg.HKEY_CURRENT_USER
    base = r"Software\Classes\*\shell\Subsearch"
    command = rf"{base}\command"
    return hive, base, command


def ensure_context_menu_keys() -> None:
    hive, base, command = _context_menu_paths()
    _ensure_key(hive, base)
    _ensure_key(hive, command)


def set_context_menu_value(kind: str, value_data: str | None = None) -> None:
    hive, base, command = _context_menu_paths()
    if kind == "menu_text":
        _set_value(hive, base, None, value_data or _default_menu_text())
        return
    if kind == "icon":
        _set_value(hive, base, "Icon", value_data or _default_icon_path())
        return
    if kind == "applies_to":
        if value_data is None:
            return
        _set_value(hive, base, "AppliesTo", value_data)
        return
    if kind == "command":
        _set_value(hive, command, None, value_data or _default_command())
        return


def write_context_menu_value(key_type: str) -> None:
    mapping: dict[str, tuple[str, str | None]] = {
        "subsearch": ("menu_text", None),
        "icon": ("icon", None),
        "appliesto": ("applies_to", None),
        "command": ("command", None),
    }
    kind, data = mapping.get(key_type, ("", None))
    if kind:
        set_context_menu_value(kind, data)


def write_all_context_menu_values() -> None:
    for key in ("subsearch", "icon", "appliesto", "command"):
        write_context_menu_value(key)


def install_context_menu() -> None:
    ensure_context_menu_keys()
    write_all_context_menu_values()