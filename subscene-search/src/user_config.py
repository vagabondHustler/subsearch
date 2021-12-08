# setup_subscene
import ctypes
import sys
import os

from src.tools.os import root_directory_file
from src.tools.current_user import is_admin
from src.tools.regkey import write_key


def context_menu() -> None:
    if is_admin():
        write_key()
        os.system(f'cmd /c "reg import regkey.reg"')
    else:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)


def select_language():
    print("For example: English")
    language = input("Enter subtitle search filter language: ")
    with open(root_directory_file("config/language.txt"), "w", encoding="utf-8") as f:
        line = f.writelines(language)
        return line
