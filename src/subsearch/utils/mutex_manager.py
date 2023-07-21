import ctypes
from typing import Callable

from subsearch.data import __guid__
from subsearch.utils import exceptions, io_json


def apply_mutex(func: Callable) -> Callable:
    """
    A decorator for safe concurrent code execution.

    Args:
        mutex_name (str): The name of the mutex.

    Returns:
        Callable: A decorated function that is synchronized using the named mutex.

    Raises:
        MultipleInstancesError: If another instance of the application is already running.

    """

    def inner(*args, **kwargs):
        try:
            if io_json.get_json_key("multiple_app_instances"):
                return func()
        except FileNotFoundError:
            pass
        except KeyError:
            pass
        kernel32 = ctypes.WinDLL("kernel32")
        mutex = kernel32.CreateMutexW(None, False, __guid__)
        last_error = kernel32.GetLastError()

        if last_error == 183:
            raise exceptions.MultipleInstancesError(__guid__)
        try:
            kernel32.WaitForSingleObject(mutex, -1)
            return func(*args, **kwargs)
        finally:
            kernel32.ReleaseMutex(mutex)

    return inner
