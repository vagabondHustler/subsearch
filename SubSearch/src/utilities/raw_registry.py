import os
import socket
import sys
import winreg

from src.utilities import current_user, local_paths

COMPUTER_NAME = socket.gethostname()
ASTERISK_PATH = r"Software\Classes\*"
SHELL_PATH = r"Software\Classes\*\shell"
SUBSEARCH_PATH = r"Software\Classes\*\shell\0.SubSearch"
COMMAND_PATH = r"Software\Classes\*\shell\0.SubSearch\command"


def write_keys():
    with winreg.ConnectRegistry(COMPUTER_NAME, winreg.HKEY_CURRENT_USER) as hkey:
        # open key, with write permission
        with winreg.OpenKey(hkey, ASTERISK_PATH, 0, winreg.KEY_WRITE) as sk:
            winreg.CreateKey(sk, "shell")
        with winreg.OpenKey(hkey, SHELL_PATH, 0, winreg.KEY_WRITE) as sk:
            winreg.CreateKey(sk, "0.SubSearch")
        with winreg.OpenKey(hkey, SUBSEARCH_PATH, 0, winreg.KEY_WRITE) as sk:
            winreg.CreateKey(sk, "command")


def write_all_valuex():
    write_valuex("SubSearch")
    write_valuex("icon")
    write_valuex("appliesto")
    if current_user.is_exe() is False:
        write_valuex("command")


def write_valuex(key: str):
    """
    Args:
        key: icon, appliesto or command
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


def open_write_valuex(sub_key: str, value_name: str, value: str):
    """
    Args:
        sub_key: 0.SubSearch or command
        value_name: Icon, AppliesTo or ""
        value: str
    """
    # connect to Computer_NAME\HKEY_CURRENT_USER\
    with winreg.ConnectRegistry(COMPUTER_NAME, winreg.HKEY_CURRENT_USER) as hkey:
        # open key, with write permission
        with winreg.OpenKey(hkey, sub_key, 0, winreg.KEY_WRITE) as sk:
            # write valuex to matching value name
            winreg.SetValueEx(sk, value_name, 0, winreg.REG_SZ, value)


def get_command_value():
    # get latest json value from file
    from src.utilities import raw_config

    show_terminal = raw_config.get("show_terminal")
    if current_user.is_exe():
        exe_path = local_paths.get_path("cwd")
        value = f'"{exe_path}\SubSearch.exe" %1'
        # if SubSearch is compiled we dont need anything besides this
    elif current_user.is_exe() is False:
        # gets the location to the python executable
        python_path = os.path.dirname(sys.executable)
        # sys.args[-1] is going to be the path to the file we right clicked on
        # import_sys = "import sys; media_file_path = sys.argv[-1];"
        set_title = "import ctypes; ctypes.windll.kernel32.SetConsoleTitleW('SubSearch');"
        # gets the path of the root directory of subsearch
        set_wd = f"import os; working_path = os.getcwd(); os.chdir('{local_paths.get_path('root')}');"
        import_main = "import main; os.chdir(working_path); main.main()"
        if show_terminal == "True":
            value = f'{python_path}\python.exe -c "{set_title} {set_wd} {import_main}" %1'
        if show_terminal == "False":
            value = f'{python_path}\pythonw.exe -c "{set_title} {set_wd} {import_main}" %1'

    return value


def get_icon_value():
    # get latest json value from file
    from src.utilities import raw_config

    show_icon: str = raw_config.get("cm_icon")
    icon_path = local_paths.get_path("icons", "16.ico")
    if show_icon == "True":
        value = icon_path
    if show_icon == "False":
        value = ""
    return value


def get_appliesto_value():
    # get latest json value from file
    from src.utilities import raw_config

    video_ext = raw_config.get("video_ext")
    vide_ext_items = len(video_ext)
    # for which file types to show the SubSearch context entry on
    value = ""
    for i, num in zip(video_ext, range(0, vide_ext_items)):
        if num == vide_ext_items - 1:
            value += "".join(f'"{i}"')
        else:
            value += "".join(f'"{i}" OR ')

    return value


def remove_context_menu():
    with winreg.ConnectRegistry(COMPUTER_NAME, winreg.HKEY_CURRENT_USER) as hkey:
        with winreg.OpenKey(hkey, SUBSEARCH_PATH, 0, winreg.KEY_WRITE) as sk:
            winreg.DeleteKey(sk, "command")

    with winreg.ConnectRegistry(COMPUTER_NAME, winreg.HKEY_CURRENT_USER) as hkey:
        with winreg.OpenKey(hkey, SHELL_PATH, 0, winreg.KEY_WRITE) as sk:
            winreg.DeleteKey(sk, "0.SubSearch")


# write keys to registry then write values
def add_context_menu():
    write_keys()
    write_all_valuex()
