import ctypes
import functools
import sys
from typing import Any, Callable

from subsearch.globals import exceptions
from subsearch.globals.constants import FILE_PATHS, GUID
from subsearch.utils import io_toml

enable_system_tray: bool


class SingleInstanceManager:
    def __init__(self, guid: str):
        self.guid = guid
        self._kernel32 = None

    @property
    def kernel32(self) -> ctypes.WinDLL:
        if self._kernel32 is None:
            self._kernel32 = ctypes.WinDLL("kernel32")
        return self._kernel32

    def is_multi_instance_allowed(self) -> bool:
        try:
            return not io_toml.load_toml_value(FILE_PATHS.config, "misc.single_instance")
        except (FileNotFoundError, KeyError, TypeError):
            return False

    def _acquire_mutex(self):
        mutex = self.kernel32.CreateMutexW(None, False, self.guid)
        if self.kernel32.GetLastError() == 183:  # ERROR_ALREADY_EXISTS
            raise exceptions.MultipleInstancesError(self.guid)
        self.kernel32.WaitForSingleObject(mutex, -1)
        return mutex

    def _release_mutex(self, mutex):
        self.kernel32.ReleaseMutex(mutex)

    def apply_mutex(self, func: Callable) -> Callable:
        def wrapper(*args, **kwargs) -> Any:
            if self.is_multi_instance_allowed():
                return func(*args, **kwargs)

            mutex = self._acquire_mutex()
            try:
                return func(*args, **kwargs)
            finally:
                self._release_mutex(mutex)

        return wrapper


def apply_mutex(func: Callable[..., Any]) -> Callable[..., Any]:
    manager = SingleInstanceManager(guid=GUID)
    return manager.apply_mutex(func)


def check_option_disabled(func) -> Callable[..., Any]:
    def wrapper(self, event, *args, **kwargs) -> Any:
        btn = event.widget
        if btn.instate(["disabled"]):
            return None
        return func(self, event, *args, **kwargs)

    return wrapper


def call_func(func) -> Callable[..., Any]:

    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        func_name = f"{func.__name__}"
        if not args[0].call_conditions.call_func(func_name=func_name, *args, **kwargs):
            return None
        return func(*args, **kwargs)

    return wrapper


def system_tray_conditions(func) -> Callable[..., Any]:
    def wrapper(*args, **kwargs) -> Any:
        if enable_system_tray:
            return func(*args, **kwargs)

    return wrapper


def except_hook(func, excepthook_) -> Callable[..., Any]:
    def wrapper(*args, **kwargs) -> Any:
        sys.excepthook = excepthook_
        return func(*args, **kwargs)

    return wrapper


def optional_hook(func):
    """Decorator to mark methods as optional hooks (no-op by default)."""
    return func
