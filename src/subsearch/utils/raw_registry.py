import os
import socket
import sys
import winreg
from typing import Literal

from subsearch.data import __icons__, __root__
from subsearch.utils import current_user

COMPUTER_NAME = socket.gethostname()
ASTERISK_PATH = "Software\\Classes\\*"
SHELL_PATH = "Software\\Classes\\*\\shell"
SUBSEARCH_PATH = "Software\\Classes\\*\\shell\\0.SubSearch"
COMMAND_PATH = "Software\\Classes\\*\\shell\\0.SubSearch\\command"


def write_keys() -> None:
    """
    Write the necessary keys to the registry
    """
    with winreg.ConnectRegistry(COMPUTER_NAME, winreg.HKEY_CURRENT_USER) as hkey:
        # open key, with write permission
        with winreg.OpenKey(hkey, ASTERISK_PATH, 0, winreg.KEY_WRITE) as sk:
            winreg.CreateKey(sk, "shell")
        with winreg.OpenKey(hkey, SHELL_PATH, 0, winreg.KEY_WRITE) as sk:
            winreg.CreateKey(sk, "0.SubSearch")
        with winreg.OpenKey(hkey, SUBSEARCH_PATH, 0, winreg.KEY_WRITE) as sk:
            winreg.CreateKey(sk, "command")


def write_all_valuex() -> None:
    write_valuex("SubSearch")
    write_valuex("icon")
    write_valuex("appliesto")
    write_valuex("command")


def write_valuex(key: str) -> None:
    """
    Write valuex into the different keys

    """
    # decide in which registry key to write the value
    if key == "SubSearch":
        key_type = SUBSEARCH_PATH
        value_name = ""
        value = "SubSearch"
    if key.lower() == "icon":
        key_type = SUBSEARCH_PATH
        value_name = "Icon"
        value = get_icon_value()
    elif key.lower() == "appliesto":
        key_type = SUBSEARCH_PATH
        value_name = "AppliesTo"
        value = get_appliesto_value()
    elif key.lower() == "command":
        key_type = COMMAND_PATH
        value_name = ""
        value = get_command_value()
    open_write_valuex(key_type, value_name, value)


def open_write_valuex(sub_key: str, value_name: str, value: str) -> None:
    """
    Connects to the registry, opens sub-key then set valuex with value
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
    Get the correct command value
    """
    # get latest json value from file
    from subsearch.utils import raw_config

    if current_user.check_is_exe():
        value = f'"{sys.argv[0]}" "%1"'
        # if SubSearch is compiled we dont need anything besides this
    elif current_user.check_is_exe() is False:
        show_terminal = raw_config.get("show_terminal")
        # gets the location to the python executable
        python_path = os.path.dirname(sys.executable)
        # sys.args[-1] is going to be the path to the file we right clicked on
        # import_sys = "import sys; media_file_path = sys.argv[-1];"
        set_title = "import ctypes; ctypes.windll.kernel32.SetConsoleTitleW('SubSearch');"
        # gets the path of the root directory of subsearch
        set_wd = f"import os; os.chdir(r'{__root__}');"
        import_main = "import subsearch; subsearch.main()"
        if show_terminal is True:
            value = f'{python_path}\python.exe -c "{set_title} {set_wd} {import_main}" "%1"'
        if show_terminal is False:
            value = f'{python_path}\pythonw.exe -c "{set_title} {set_wd} {import_main}" "%1"'

    return value


def get_icon_value() -> str:
    """
    Check config.json cm_icon value

    """
    from subsearch.utils import raw_config

    show_icon: str = raw_config.get("cm_icon")
    icon_path = os.path.join(__icons__, "16.ico")
    if show_icon:
        return icon_path
    else:
        return ""


def get_appliesto_value() -> str:
    # get latest json value from file
    from subsearch.utils import raw_config

    file_ext = raw_config.get("file_ext")
    # for which file types to show the SubSearch context entry on
    value = '"subsearch.py" OR '
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
            winreg.DeleteKey(sk, "0.SubSearch")


# write keys to registry then write values
def add_context_menu() -> None:
    write_keys()
    write_all_valuex()
