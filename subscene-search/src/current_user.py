import winreg as reg
import ctypes
import os


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


# def got_file() -> bool:
#     if os.path.isfile(frp("language")) and os.stat(frp("language")).st_size != 0:
#         return True
#     else:
#         return False
