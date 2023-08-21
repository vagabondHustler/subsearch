import socket
import sys
import winreg
from pathlib import Path

from subsearch.data.constants import APP_PATHS, DEVICE_INFO, FILE_PATHS
from subsearch.utils import io_toml

COMPUTER_NAME = socket.gethostname()
CLASSES_PATH = r"Software\Classes"
ASTERISK_PATH = r"Software\Classes\*"
SHELL_PATH = r"Software\Classes\*\shell"
SUBSEARCH_PATH = r"Software\Classes\*\shell\Subsearch"
COMMAND_PATH = r"Software\Classes\*\shell\Subsearch\command"


def write_keys() -> None:
    key_paths = [(CLASSES_PATH, "*"), (ASTERISK_PATH, "shell"), (SHELL_PATH, "Subsearch"), (SUBSEARCH_PATH, "command")]
    with winreg.ConnectRegistry(COMPUTER_NAME, winreg.HKEY_CURRENT_USER) as hkey:
        for path, sub_key in key_paths:
            with winreg.OpenKey(hkey, path, 0, winreg.KEY_WRITE) as sk:
                winreg.CreateKey(sk, sub_key)


def write_all_valuex() -> None:
    items = ["subsearch", "icon", "appliesto", "command"]
    for i in items:
        write_valuex(i)


def write_valuex(key: str) -> None:
    key_map = {
        "subsearch": {"key_type": SUBSEARCH_PATH, "value_name": "", "value": "Subsearch"},
        "icon": {"key_type": SUBSEARCH_PATH, "value_name": "Icon", "value": get_icon_value()},
        "appliesto": {"key_type": SUBSEARCH_PATH, "value_name": "AppliesTo", "value": get_appliesto_value()},
        "command": {"key_type": COMMAND_PATH, "value_name": "", "value": get_command_value()},
    }

    key = key.lower()
    if key in key_map:
        key_type = key_map[key]["key_type"]
        value_name = key_map[key]["value_name"]
        value = key_map[key]["value"]
        open_write_valuex(key_type, value_name, value)


def open_write_valuex(sub_key: str, value_name: str, value: str) -> None:
    try:
        # connect to Computer_NAME\HKEY_CURRENT_USER\
        with winreg.ConnectRegistry(COMPUTER_NAME, winreg.HKEY_CURRENT_USER) as hkey:
            # open key, with write permission
            with winreg.OpenKey(hkey, sub_key, 0, winreg.KEY_WRITE) as sk:
                # write valuex to matching value name
                winreg.SetValueEx(sk, value_name, 0, winreg.REG_SZ, value)
    except FileNotFoundError:
        pass


def get_command_value() -> str:
    # get latest toml value from file
    from subsearch.utils import io_toml

    if DEVICE_INFO.mode == "executable":
        value = f'"{sys.argv[0]}" "%1"'
        # if SubSearch is compiled we dont need anything besides this
    elif DEVICE_INFO.mode == "interpreter":
        show_terminal = io_toml.load_toml_value(FILE_PATHS.config, "gui.show_terminal")
        # gets the location to the python executable
        python_path = Path(sys.executable).parent
        # sys.args[-1] is going to be the path to the file we right clicked on
        # import_sys = "import sys; media_file_path = sys.argv[-1];"
        set_title = "import ctypes; ctypes.windll.kernel32.SetConsoleTitleW('subsearch');"
        # gets the path of the root directory of subsearch
        set_wd = f"import os; os.chdir(r'{APP_PATHS.home}');"
        import_main = "import subsearch; subsearch.main()"
        if show_terminal is True:
            value = f'{python_path}\python.exe -c "{set_title} {set_wd} {import_main}" "%1"'
        if show_terminal is False:
            value = f'{python_path}\pythonw.exe -c "{set_title} {set_wd} {import_main}" "%1"'

    return value


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


def remove_context_menu() -> None:
    with winreg.ConnectRegistry(COMPUTER_NAME, winreg.HKEY_CURRENT_USER) as hkey:
        with winreg.OpenKey(hkey, SUBSEARCH_PATH, 0, winreg.KEY_WRITE) as sk:
            winreg.DeleteKey(sk, "command")

    with winreg.ConnectRegistry(COMPUTER_NAME, winreg.HKEY_CURRENT_USER) as hkey:
        with winreg.OpenKey(hkey, SHELL_PATH, 0, winreg.KEY_WRITE) as sk:
            winreg.DeleteKey(sk, "Subsearch")



def add_context_menu() -> None:
    write_keys()
    write_all_valuex()


def registry_key_exists() -> bool:
    sub_key = rf"Software\Classes\*\shell\Subsearch\command"
    try:
        with winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER) as hkey:
            winreg.OpenKey(hkey, sub_key)
            return True
    except Exception:
        return False


def key_no_value() -> bool:
    sub_key = rf"Software\Classes\*\shell\Subsearch\command"
    with winreg.ConnectRegistry(COMPUTER_NAME, winreg.HKEY_CURRENT_USER) as hkey:
        with winreg.OpenKey(hkey, sub_key) as subkey:
            default = winreg.QueryValueEx(subkey, None)  # type: ignore
            if default[0] == "":
                return True
    return False
