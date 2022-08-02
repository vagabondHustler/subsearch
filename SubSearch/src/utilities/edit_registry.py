import os
import socket
import sys
import winreg

from src.utilities import local_paths, current_user

COMPUTER_NAME = socket.gethostname()

# write value to "Icon"
def set_context_menu_icon():
    from src.utilities import read_config

    use: str = read_config.get("cm_icon")
    subsearch_path = r"Software\Classes\*\shell\0.SubSearch"
    icon_path = local_paths.get_path("icons", "16.ico")
    with winreg.ConnectRegistry(COMPUTER_NAME, winreg.HKEY_CURRENT_USER) as hkey:
        with winreg.OpenKey(hkey, subsearch_path, 0, winreg.KEY_WRITE) as subkey_ss:
            if use == "True":
                winreg.SetValueEx(subkey_ss, "Icon", 0, winreg.REG_SZ, icon_path)
            if use == "False":
                winreg.SetValueEx(subkey_ss, "Icon", 0, winreg.REG_SZ, "")


# write value to (Default)
def write_command_subkey():
    from src.utilities import read_config

    show_terminal = read_config.get("show_terminal")
    video_ext = read_config.get("video_ext")
    vide_ext_items = len(video_ext)

    # for which file types to show the SubSearch context entry on
    appliesto_value = ""
    for i, num in zip(video_ext, range(0, vide_ext_items)):
        if num == vide_ext_items - 1:
            appliesto_value += "".join(f'"{i}"')
        else:
            appliesto_value += "".join(f'"{i}" OR ')

    # registry paths for SubSearch
    subsearch_path = r"Software\Classes\*\shell\0.SubSearch"
    # registry paths for what SubSearch does when pressed in context menu
    command_path = r"Software\Classes\*\shell\0.SubSearch\command"
    if current_user.is_exe():
        # if SubSearch is compiled we dont need anything besides this
        exe_path = local_paths.get_path('cwd')
        exe_version = f'"{exe_path}\SubSearch.exe" %1'
    else:
        # gets the location to the python executable
        python_path = os.path.dirname(sys.executable)
        # sys.args[-1] is going to be the path to the file we right clicked on
        # import_sys = "import sys; media_file_path = sys.argv[-1];"
        set_title = "import ctypes; ctypes.windll.kernel32.SetConsoleTitleW('SubSearch');"
        # gets the path of the root directory of subsearch
        set_wd = f"import os; working_path = os.getcwd(); os.chdir('{local_paths.get_path('root')}');"
        run_main = "import main; os.chdir(working_path); main.main()"

        terminal_true = (
            f'{python_path}\python.exe -c "{set_title} {set_wd} {run_main}" %1'  # %1 is the path to the file
        )
        terminal_false = f'{python_path}\pythonw.exe -c "{set_title} {set_wd} {run_main}" %1'

    # set the command value
    with winreg.ConnectRegistry(COMPUTER_NAME, winreg.HKEY_CURRENT_USER) as hkey:
        with winreg.OpenKey(hkey, command_path, 0, winreg.KEY_WRITE) as subkey:
            if current_user.is_exe():
                winreg.SetValueEx(subkey, "", 0, winreg.REG_SZ, exe_version)
            elif show_terminal == "True" and current_user.is_exe() is False:
                winreg.SetValueEx(subkey, "", 0, winreg.REG_SZ, terminal_true)
            elif show_terminal == "False" and current_user.is_exe() is False:
                winreg.SetValueEx(subkey, "", 0, winreg.REG_SZ, terminal_false)

    # set the AppliesTo value
    with winreg.ConnectRegistry(COMPUTER_NAME, winreg.HKEY_CURRENT_USER) as hkey:
        with winreg.OpenKey(hkey, subsearch_path, 0, winreg.KEY_WRITE) as subkey:
            winreg.SetValueEx(subkey, "AppliesTo", 0, winreg.REG_SZ, appliesto_value)

    set_context_menu_icon()


def restore_context_menu():
    regkey = local_paths.get_path("data", "regkey.reg")
    os.system(f'cmd /c "reg import "{regkey}"')
    set_context_menu_icon()
    write_command_subkey()


def remove_context_menu():
    shell_path = r"Software\Classes\*\shell"
    ss_path = r"Software\Classes\*\shell\0.SubSearch"

    with winreg.ConnectRegistry(COMPUTER_NAME, winreg.HKEY_CURRENT_USER) as hkey:
        with winreg.OpenKey(hkey, ss_path, 0, winreg.KEY_WRITE) as ss_key:
            winreg.DeleteKey(ss_key, "command")

    with winreg.ConnectRegistry(COMPUTER_NAME, winreg.HKEY_CURRENT_USER) as hkey:
        with winreg.OpenKey(hkey, shell_path, 0, winreg.KEY_WRITE) as shell_key:
            winreg.DeleteKey(shell_key, "0.SubSearch")


# imports empty registry key to be filled in with values later
def add_context_menu():
    regkey = local_paths.get_path("data", "regkey.reg")
    os.system(f'cmd /c "reg import "{regkey}"')
    set_context_menu_icon()
    write_command_subkey()
