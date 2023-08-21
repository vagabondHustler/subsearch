import sys
import winreg
from pathlib import Path

from subsearch.data.constants import (
    APP_PATHS,
    COMPUTER_NAME,
    DEVICE_INFO,
    FILE_PATHS,
    REGISTRY_PATHS,
)
from subsearch.utils import io_toml


class LaunchOptions:
    def __init__(self) -> None:
        self.show_terminal = io_toml.load_toml_value(FILE_PATHS.config, "gui.show_terminal")
        self.python_path = Path(sys.executable).parent
        self.console_title = "import ctypes; ctypes.windll.kernel32.SetConsoleTitleW('subsearch');"
        self.working_directory = f"import os; os.chdir(r'{APP_PATHS.home}');"
        self.import_subsearch = "import subsearch; subsearch.main()"

    def _get_mode_executable(self) -> str:
        return f'"{sys.argv[0]}" "%1"'

    def _get_mode_interpreter(self) -> str:
        python_executable = {
            True: f'{self.python_path}\python.exe -c "{self.console_title} {self.working_directory} {self.import_subsearch}" "%1"',
            False: f'{self.python_path}\pythonw.exe -c "{self.console_title} {self.working_directory} {self.import_subsearch}" "%1"',
        }
        return python_executable[self.show_terminal]

    def get_parameter(self) -> str:
        if DEVICE_INFO.mode == "executable":
            value = self._get_mode_executable()
        elif DEVICE_INFO.mode == "interpreter":
            value = self._get_mode_interpreter()
        return value


def get_command_value() -> str:
    launch_options = LaunchOptions()
    return launch_options.get_parameter()


def get_icon_value() -> str:
    show_icon: str = io_toml.load_toml_value(FILE_PATHS.config, "gui.context_menu_icon")
    if show_icon:
        return str(APP_PATHS.gui_assets / "subsearch.ico")
    else:
        return ""


def get_appliesto_value() -> str:
    file_ext = io_toml.load_toml_value(FILE_PATHS.config, "file_extensions")
    value = ""
    for ext, v in zip(file_ext.keys(), file_ext.values()):
        if v is True:
            value += "".join(f'".{ext}" OR ')
    if value.endswith(" OR "):  # remove last OR
        value = value[:-4]

    return value


def del_registry_key(reg_path: str, key: str) -> None:
    with winreg.ConnectRegistry(COMPUTER_NAME, winreg.HKEY_CURRENT_USER) as hkey:
        with winreg.OpenKey(hkey, reg_path, 0, winreg.KEY_WRITE) as sk:
            winreg.DeleteKey(sk, key)


def del_context_menu() -> None:
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
            with winreg.OpenKey(hkey, key, 0, winreg.KEY_WRITE) as sk:
                winreg.CreateKey(sk, sub_key)


def set_write_valuex(sub_key: str, value_name: str, value: str) -> None:
    try:
        with winreg.ConnectRegistry(COMPUTER_NAME, winreg.HKEY_CURRENT_USER) as hkey:
            with winreg.OpenKey(hkey, sub_key, 0, winreg.KEY_WRITE) as sk:
                winreg.SetValueEx(sk, value_name, 0, winreg.REG_SZ, value)
    except FileNotFoundError:
        pass


def write_valuex(key: str) -> None:
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
        set_write_valuex(key_type, value_name, value)


def write_all_valuex() -> None:
    items = ["subsearch", "icon", "appliesto", "command"]
    for i in items:
        write_valuex(i)


def add_context_menu() -> None:
    write_keys()
    write_all_valuex()
