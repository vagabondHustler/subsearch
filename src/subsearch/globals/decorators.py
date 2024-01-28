import ctypes
from datetime import datetime
import inspect
from typing import Any, Callable

from subsearch.globals import exceptions
from subsearch.globals import metaclasses
from subsearch.globals.constants import FILE_PATHS, GUID
from subsearch.utils import io_toml

enable_system_tray: bool


def apply_mutex(func: Callable) -> Callable:
    def inner(*args, **kwargs) -> Any:
        try:
            if not io_toml.load_toml_value(FILE_PATHS.config, "misc.single_instance"):
                return func()
        except FileNotFoundError:
            pass
        except KeyError:
            pass
        except TypeError:
            pass
        kernel32 = ctypes.WinDLL("kernel32")
        mutex = kernel32.CreateMutexW(None, False, GUID)
        last_error = kernel32.GetLastError()

        if last_error == 183:
            raise exceptions.MultipleInstancesError(GUID)
        try:
            kernel32.WaitForSingleObject(mutex, -1)
            return func(*args, **kwargs)
        finally:
            kernel32.ReleaseMutex(mutex)

    return inner


def check_option_disabled(func) -> Callable:
    def wrapper(self, event, *args, **kwargs) -> Any:
        btn = event.widget
        if btn.instate(["disabled"]):
            return None
        return func(self, event, *args, **kwargs)

    return wrapper


def call_func(func) -> Callable:
    def wrapper(*args, **kwargs) -> Any:
        func_name = f"{func.__name__}"
        if not metaclasses.SubsearchFuncCondtitons.conditions_met(func_name=func_name, *args, **kwargs):
            return None
        return func(*args, **kwargs)

    return wrapper


def capture_call_info(func):
    def wrapper(*args, **kwargs):
        frame = inspect.currentframe().f_back
        current_time = datetime.now().time()
        call_time = current_time.strftime("%H:%M:%S.%f")[:-3]
        kwargs["call_module"] = frame.f_globals["__name__"].split(".")[-1]
        kwargs["call_lineno"] = frame.f_lineno
        kwargs["call_ct"] = call_time
        return func(*args, **kwargs)

    return wrapper


def system_tray_conditions(func) -> Callable:
    def wrapper(*args, **kwargs) -> Any:
        if enable_system_tray:
            return func(*args, **kwargs)

    return wrapper
