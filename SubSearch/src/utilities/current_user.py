import ctypes
import sys
import winreg as reg
import os
from src.utilities.local_paths import cwd

# check if current user has the registry key
def got_key() -> bool:
    """
    got_key returns True if the current user is has the registry key SubSearch

    Returns: True or False
    """
    sub_key = r"Software\Classes\Directory\Background\shell\SubSearch"
    try:
        with reg.ConnectRegistry(None, reg.HKEY_CURRENT_USER) as hkey:
            reg.OpenKey(hkey, sub_key)
    except Exception:
        return False

#* removed this function as it no longer used
#* if context menu item is written to HKEY_CURRENT_USER there are no need for admin privileges
# check if the current user is running .py as admin
# def is_admin() -> bool:
#     try:
#         return ctypes.windll.shell32.IsUserAnAdmin()
#     except PermissionError:
#         return False


# re-run .py as admin
# def run_as_admin():
#     _python_exe = sys.executable
#     _pythonw_exe = _python_exe.replace("python.exe", "pythonw.exe")
#     ctypes.windll.shell32.ShellExecuteW(None, "runas", _pythonw_exe, " ".join(sys.argv), None, 1)


def is_exe_version() -> bool:
    """
    is_exe_version returns True if the current user is running SubSearch from  executable

    Returns: True or False
    """
    
    for file in os.listdir(cwd()):
        if file.endswith("SubSearch.exe"):
            return True
    return False
