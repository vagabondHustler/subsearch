import os
import winreg
import socket

from src.config import get
from src.sos import root_directory
from src.current_user import is_admin
from src.current_user import run_as_admin

COMPUTER_NAME = socket.gethostname()


def context_menu_icon(use=get("cm_icon")):
    ss_path = "Directory\Background\shell\Search subscene"
    icon_path = f"{root_directory()}\icon.ico, 0"
    with winreg.ConnectRegistry(COMPUTER_NAME, winreg.HKEY_CLASSES_ROOT) as hkey:
        with winreg.OpenKey(hkey, ss_path, 0, winreg.KEY_ALL_ACCESS) as subkey_ss:
            if use == "True":
                winreg.SetValueEx(subkey_ss, "Icon", 0, winreg.REG_SZ, icon_path)
            if use == "False":
                winreg.DeleteValue(subkey_ss, "Icon")


def write_command_subkey():
    from src.config import get

    open_with = get("terminal_in")
    focus = get("terminal_focus")

    command_path = "Directory\Background\shell\Search subscene\command"
    main_path = f"{root_directory()}\main.py"

    terminal_title = '"& {$host.ui.RawUI.WindowTitle = ' + "'Subscene search'" + '}"'
    pwsh = f"pwsh.exe -noexit -command {terminal_title} Set-Location -literalPath '%V'; python {main_path} -NoNewWindow"
    pwsh_silent = f"pwsh.exe -command {terminal_title} Set-Location -literalPath '%V'; pythonw {main_path} -NoNewWindow"

    ps = pwsh.replace("pwsh.exe", "powershell.exe")
    ps_silent = pwsh_silent.replace("pwsh.exe", "powershell.exe")

    cmd = f'cmd.exe "%V" /c start /min python {main_path}'
    cmd_silent = cmd.replace("/min ", "")

    with winreg.ConnectRegistry(COMPUTER_NAME, winreg.HKEY_CLASSES_ROOT) as hkey:
        with winreg.OpenKey(hkey, command_path, 0, winreg.KEY_ALL_ACCESS) as subkey_command:
            if open_with == "pwsh":
                if focus == "True":
                    winreg.SetValueEx(subkey_command, "", 0, winreg.REG_SZ, pwsh)
                elif focus == "False":
                    winreg.SetValueEx(subkey_command, "", 0, winreg.REG_SZ, pwsh_silent)
            elif open_with == "ps":
                if focus == "True":
                    winreg.SetValueEx(subkey_command, "", 0, winreg.REG_SZ, ps)
                elif focus == "False":
                    winreg.SetValueEx(subkey_command, "", 0, winreg.REG_SZ, ps_silent)

            elif open_with == "cmd":
                if focus == "True":
                    winreg.SetValueEx(subkey_command, "", 0, winreg.REG_SZ, cmd)
                elif focus == "False":
                    winreg.SetValueEx(subkey_command, "", 0, winreg.REG_SZ, cmd_silent)


def add_context_menu() -> None:
    if is_admin():
        os.system(f'cmd /c "reg import regkey.reg"')
        context_menu_icon()
        write_command_subkey()
    else:
        run_as_admin()
