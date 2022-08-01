import os
import socket
import sys
import winreg

from src.utilities import local_paths, current_user

COMPUTER_NAME = socket.gethostname()

# write value to "Icon"
def context_menu_icon():
    from src.utilities import read_config

    use: str = read_config.get("cm_icon")
    ss_path = "Software\Classes\Directory\Background\shell\SubSearch"
    icon_path = local_paths.root_directory("data", "16.ico")
    with winreg.ConnectRegistry(COMPUTER_NAME, winreg.HKEY_CURRENT_USER) as hkey:
        with winreg.OpenKey(hkey, ss_path, 0, winreg.KEY_WRITE) as subkey_ss:
            if use == "True":
                winreg.SetValueEx(subkey_ss, "Icon", 0, winreg.REG_SZ, icon_path)
            if use == "False":
                winreg.SetValueEx(subkey_ss, "Icon", 0, winreg.REG_SZ, "")


# write value to (Default)
def write_command_subkey():
    from src.utilities import read_config

    focus = read_config.get("show_terminal")

    command_path = "Software\Classes\Directory\Background\shell\SubSearch\command"
    if current_user.is_exe():
        exe_path = local_paths.root_directory(file_name="SubSearch.exe")
    else:
        python_path = os.path.dirname(sys.executable)
        set_title = "import ctypes; ctypes.windll.kernel32.SetConsoleTitleW('SubSearch');"
        set_wd = f"import os; working_path = os.getcwd(); os.chdir('{local_paths.root_directory()}');"
        run_main = "import main; os.chdir(working_path); main.main()"

        tfocus = f'{python_path}\python.exe -c "{set_title} {set_wd} {run_main}"'
        tsilent = f'{python_path}\pythonw.exe -c "{set_title} {set_wd} {run_main}"'

    with winreg.ConnectRegistry(COMPUTER_NAME, winreg.HKEY_CURRENT_USER) as hkey:
        with winreg.OpenKey(hkey, command_path, 0, winreg.KEY_WRITE) as subkey_command:
            if current_user.is_exe():
                winreg.SetValueEx(subkey_command, "", 0, winreg.REG_SZ, exe_path)
                return
            if focus == "True":
                winreg.SetValueEx(subkey_command, "", 0, winreg.REG_SZ, tfocus)
                return
            if focus == "False":
                winreg.SetValueEx(subkey_command, "", 0, winreg.REG_SZ, tsilent)
                return


def restore_context_menu():
    regkey = local_paths.root_directory("data", "regkey.reg")
    os.system(f'cmd /c "reg import "{regkey}"')
    context_menu_icon()
    write_command_subkey()


def remove_context_menu():
    shell_path = "Software\Classes\Directory\Background\shell"
    ss_path = "Software\Classes\Directory\Background\shell\SubSearch"

    with winreg.ConnectRegistry(COMPUTER_NAME, winreg.HKEY_CURRENT_USER) as hkey:
        with winreg.OpenKey(hkey, ss_path, 0, winreg.KEY_WRITE) as ss_key:
            winreg.DeleteKey(ss_key, "command")

    with winreg.ConnectRegistry(COMPUTER_NAME, winreg.HKEY_CURRENT_USER) as hkey:
        with winreg.OpenKey(hkey, shell_path, 0, winreg.KEY_WRITE) as shell_key:
            winreg.DeleteKey(shell_key, "SubSearch")


# imports empty registry key to be filled in with values later
def add_context_menu():
    regkey = local_paths.root_directory("data", "regkey.reg")
    os.system(f'cmd /c "reg import "{regkey}"')
    context_menu_icon()
    write_command_subkey()
