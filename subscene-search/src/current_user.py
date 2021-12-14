import winreg as reg
import ctypes
import sys

# check if current user has the registry key
def got_key() -> bool:
    sub_key = r"Directory\Background\shell\Search subscene"
    try:
        with reg.ConnectRegistry(None, reg.HKEY_CLASSES_ROOT) as hkey:
            reg.OpenKey(hkey, sub_key)
    except Exception:
        return False


# check if the current user is running .py as admin
def is_admin() -> bool:
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except PermissionError:
        return False


# re-run .py as admin
def run_as_admin() -> None:
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
