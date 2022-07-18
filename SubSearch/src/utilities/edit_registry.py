import os
import socket
import sys
import winreg

from src.utilities.local_paths import root_directory, root_directory
from src.utilities.current_user import is_admin, run_as_admin

COMPUTER_NAME = socket.gethostname()

# write value to "Icon"
def context_menu_icon() -> None:
    from src.utilities.fetch_config import get

    use: str = get("cm_icon")
    ss_path = "Directory\Background\shell\SubSearch"
    icon_path = root_directory("data", "icon.ico")
    with winreg.ConnectRegistry(COMPUTER_NAME, winreg.HKEY_CLASSES_ROOT) as hkey:
        with winreg.OpenKey(hkey, ss_path, 0, winreg.KEY_ALL_ACCESS) as subkey_ss:
            if use == "True":
                winreg.SetValueEx(subkey_ss, "Icon", 0, winreg.REG_SZ, icon_path)
            if use == "False":
                winreg.SetValueEx(subkey_ss, "Icon", 0, winreg.REG_SZ, "")


# write value to (Deafult)
def write_command_subkey() -> None:
    from src.utilities.fetch_config import get

    focus = get("terminal_focus")

    command_path = "Directory\Background\shell\SubSearch\command"

    ppath = os.path.dirname(sys.executable)
    set_title = "import ctypes; ctypes.windll.kernel32.SetConsoleTitleW('SubSearch');"
    set_wd = f"import os; working_path = os.getcwd(); os.chdir('{root_directory()}');"
    run_main = "import main; os.chdir(working_path); main.main()"

    tfocus = f'{ppath}\python.exe -c "{set_title} {set_wd} {run_main}"'
    tsilent = f'{ppath}\pythonw.exe -c "{set_title} {set_wd} {run_main}"'

    with winreg.ConnectRegistry(COMPUTER_NAME, winreg.HKEY_CLASSES_ROOT) as hkey:
        with winreg.OpenKey(hkey, command_path, 0, winreg.KEY_ALL_ACCESS) as subkey_command:
            if focus == "True":
                winreg.SetValueEx(subkey_command, "", 0, winreg.REG_SZ, tfocus)
            elif focus == "False":
                winreg.SetValueEx(subkey_command, "", 0, winreg.REG_SZ, tsilent)


def restore_context_menu() -> None:
    regkey = root_directory("data", "regkey.reg")
    os.system(f'cmd /c "reg import "{regkey}"')
    context_menu_icon()
    write_command_subkey()


def remove_context_menu() -> None:
    shell_path = "Directory\Background\shell"
    ss_path = "Directory\Background\shell\SubSearch"

    with winreg.ConnectRegistry(COMPUTER_NAME, winreg.HKEY_CLASSES_ROOT) as hkey:
        with winreg.OpenKey(hkey, ss_path, 0, winreg.KEY_ALL_ACCESS) as ss_key:
            winreg.DeleteKey(ss_key, "command")

    with winreg.ConnectRegistry(COMPUTER_NAME, winreg.HKEY_CLASSES_ROOT) as hkey:
        with winreg.OpenKey(hkey, shell_path, 0, winreg.KEY_ALL_ACCESS) as shell_key:
            winreg.DeleteKey(shell_key, "SubSearch")


# imports templet registry key to be filled in with values later
def add_context_menu() -> None:
    if is_admin():
        regkey = root_directory("data", "regkey.reg")
        os.system(f'cmd /c "reg import "{regkey}"')
        context_menu_icon()
        write_command_subkey()
    else:
        run_as_admin()
