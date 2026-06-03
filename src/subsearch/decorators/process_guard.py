import ctypes
from typing import Any, Callable

from subsearch.runtime import exceptions
from subsearch.io import toml_file
from subsearch.runtime.constants import FILE_PATHS, GUID


def apply_mutex(func: Callable) -> Callable:
    def inner(*args, **kwargs) -> Any:
        try:
            if not toml_file.load_toml_value(FILE_PATHS.config, "application.single_instance"):
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
