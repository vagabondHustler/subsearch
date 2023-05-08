import socket
import sys
import winreg
from pathlib import Path

from subsearch.data import app_paths
from subsearch.utils import file_manager

COMPUTER_NAME = socket.gethostname()
CLASSES_PATH = r"Software\Classes"
ASTERISK_PATH = r"Software\Classes\*"
SHELL_PATH = r"Software\Classes\*\shell"
SUBSEARCH_PATH = r"Software\Classes\*\shell\Subsearch"
COMMAND_PATH = r"Software\Classes\*\shell\Subsearch\command"


def write_keys() -> None:
    """
    Writes keys to the windows registry.
    """
    key_paths = [(CLASSES_PATH, "*"), (ASTERISK_PATH, "shell"), (SHELL_PATH, "Subsearch"), (SUBSEARCH_PATH, "command")]
    with winreg.ConnectRegistry(COMPUTER_NAME, winreg.HKEY_CURRENT_USER) as hkey:
        for path, sub_key in key_paths:
            with winreg.OpenKey(hkey, path, 0, winreg.KEY_WRITE) as sk:
                winreg.CreateKey(sk, sub_key)


def write_all_valuex() -> None:
    """
    Write values to the registry for `subsearch`, `icon`, `appliesto` and `command`.
    """
    items = ["subsearch", "icon", "appliesto", "command"]
    for i in items:
        write_valuex(i)


def write_valuex(key: str) -> None:
    """
    Write a value to registry key.

    Args:
        key: A string that represents the target registry key.

    Returns:
        None.
    """
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
    """
    Writes a value to a specific key in the Windows registry.

    Args:
        sub_key (str): The path of the registry key.
        value_name (str): The value name that the data will be written to.
        value (str): The data to be written to the registry.

    Raises:
        FileNotFoundError: If the specified registry key or value does not exist.
    """
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
    """
    Returns the command to execute when the context menu is used on a file for SubSearch.

    Returns:
        A string containing the command to execute for the corresponding value.
    """
    # get latest json value from file
    from subsearch.utils import io_json

    if file_manager.running_from_exe():
        value = f'"{sys.argv[0]}" "%1"'
        # if SubSearch is compiled we dont need anything besides this
    elif file_manager.running_from_exe() is False:
        show_terminal = io_json.get_json_key("show_terminal")
        # gets the location to the python executable
        python_path = Path(sys.executable).parent
        # sys.args[-1] is going to be the path to the file we right clicked on
        # import_sys = "import sys; media_file_path = sys.argv[-1];"
        set_title = "import ctypes; ctypes.windll.kernel32.SetConsoleTitleW('subsearch');"
        # gets the path of the root directory of subsearch
        set_wd = f"import os; os.chdir(r'{app_paths.home}');"
        import_main = "import subsearch; subsearch.main()"
        if show_terminal is True:
            value = f'{python_path}\python.exe -c "{set_title} {set_wd} {import_main}" "%1"'
        if show_terminal is False:
            value = f'{python_path}\pythonw.exe -c "{set_title} {set_wd} {import_main}" "%1"'

    return value


def get_icon_value() -> str:
    """
    Returns the icon path to use in the context menu, or an empty string if configuration specifies it should not be shown

    Returns:
        str: Path of the icon file to be used in the context menu, or an empty string if the configuration specifies
             that it should not be shown.
    """
    from subsearch.utils import io_json

    show_icon: str = io_json.get_json_key("context_menu_icon")
    if show_icon:
        return str(app_paths.icon)
    else:
        return ""


def get_appliesto_value() -> str:
    """
    Retrieve the latest json value from file `raw_json`.

    Returns:
        str: A string of file types to show the SubSearch context entry on
            The file types are concatenated with `" OR "` in between.
    """
    # get latest json value from file
    from subsearch.utils import io_json

    file_ext = io_json.get_json_key("file_extensions")
    # for which file types to show the SubSearch context entry on
    value = ""
    for k, v in zip(file_ext.keys(), file_ext.values()):
        if v is True:
            value += "".join(f'"{k}" OR ')
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


# write keys to registry then write values
def add_context_menu() -> None:
    write_keys()
    write_all_valuex()


def registry_key_exists() -> bool:
    """
    Check if the Subsearch context menu key is already present in the Windows registry.

    Returns:
        bool: True, If the key exists in the registry, else False.
    """
    sub_key = rf"Software\Classes\*\shell\Subsearch\command"
    try:
        with winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER) as hkey:
            winreg.OpenKey(hkey, sub_key)
            return True
    except Exception:
        return False


def key_no_value() -> bool:
    """
    Checks if the "command" value name has no value.

    Returns:
        True if the "command" value name does not have a value, False otherwise.
    """
    sub_key = rf"Software\Classes\*\shell\Subsearch\command"
    with winreg.ConnectRegistry(COMPUTER_NAME, winreg.HKEY_CURRENT_USER) as hkey:
        with winreg.OpenKey(hkey, sub_key) as subkey:
            default = winreg.QueryValueEx(subkey, None)  # type: ignore
            if default[0] == "":
                return True
    return False
