import winreg as reg
import ctypes
import sys


def got_key() -> bool:
    sub_key = r"Directory\Background\shell\Search subscene"
    try:
        with reg.ConnectRegistry(None, reg.HKEY_CLASSES_ROOT) as hkey:
            reg.OpenKey(hkey, sub_key)
    except Exception:
        return False


def is_admin() -> bool:
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except PermissionError:
        return False
    
def run_as_admin() -> None:
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)


# def got_file() -> bool:
#     if os.path.isfile(frp("language")) and os.stat(frp("language")).st_size != 0:
#         return True
#     else:
#         return False
