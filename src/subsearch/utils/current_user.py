import socket
import sys
import winreg as reg

COMPUTER_NAME = socket.gethostname()


def registry_key_exists() -> bool:
    """
    Check if current user has the registry key subsearch for the context menu

    Returns:
        bool: True if key exists, False if key does not exist
    """
    sub_key = r"Software\Classes\*\shell\0.subsearch\command"
    try:
        with reg.ConnectRegistry(None, reg.HKEY_CURRENT_USER) as hkey:
            reg.OpenKey(hkey, sub_key)
            return True
    except Exception:
        return False


def running_from_exe() -> bool:
    if sys.argv[0].endswith(".exe"):
        return True
    return False
