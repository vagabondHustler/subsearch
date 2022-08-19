import socket
import sys
import winreg as reg

COMPUTER_NAME = socket.gethostname()


def got_key() -> bool:
    """
    Check if current user has the registry key subsearch for the context menu

    Returns:
        bool: True if key exists, False if key does not exist
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
    Check if the current user is running subsearch from the executable

    Returns:
        bool: True if subsearch is running as executable, False if subsearch is not running as executable
    """

    if sys.argv[0].endswith("SubSearch.exe"):
        return True
    return False
