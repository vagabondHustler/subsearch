import os
import winreg as reg

from src.utilities import local_paths

# check if current user has the registry key
def got_key() -> bool:
    """
    got_key returns True if the current user is has the registry key SubSearch

    Returns: True or False
    """
    sub_key = r"Software\Classes\*\shell\0.SubSearch\command"
    try:
        with reg.ConnectRegistry(None, reg.HKEY_CURRENT_USER) as hkey:
            reg.OpenKey(hkey, sub_key)
    except Exception:
        return False


def is_exe() -> bool:
    """
    is_exe_version returns True if the current user is running SubSearch from  executable

    Returns: True or False
    """

    for file in os.listdir(local_paths.cwd()):
        if file.endswith("SubSearch.exe"):
            return True
    return False
