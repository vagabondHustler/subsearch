import ctypes
import sys
import winreg as reg


# check if current user has the registry key
def got_key() -> bool:
    sub_key = r"Directory\Background\shell\SubSearch"
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
    _python_exe = sys.executable
    _pythonw_exe = _python_exe.replace("python.exe", "pythonw.exe")
    ctypes.windll.shell32.ShellExecuteW(None, "runas", _pythonw_exe, " ".join(sys.argv), None, 1)
