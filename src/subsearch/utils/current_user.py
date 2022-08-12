import socket
import sys
import winreg as reg

from . import local_paths

COMPUTER_NAME = socket.gethostname()


def got_key() -> bool:
    """
    check if current user has the registry key subsearch for the context menu

    Returns
    -------
    bool
        returns True or False
    """
    sub_key = r"Software\Classes\*\shell\0.SubSearch\command"
    try:
        with reg.ConnectRegistry(None, reg.HKEY_CURRENT_USER) as hkey:
            reg.OpenKey(hkey, sub_key)
            return True
    except Exception:
        return False


def check_is_exe() -> bool:
    """
    check if the current user is running subsearch from the executable

    Returns
    -------
    bool
        returns True or False
    """

    if sys.argv[0].endswith("SubSearch.exe"):
        return True
    return False
