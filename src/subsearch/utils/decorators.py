import ctypes
import functools
import threading
from typing import Callable, Union

from subsearch import core
from subsearch.data import __guid__
from subsearch.utils import exceptions, io_json, io_log


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


def singleton(cls):
    """
    A handy decorator for creating singleton classes.

    Description:
        - Decorate your class with this decorator to ensure that only one instance of the class is created.
        - If you attempt to create another instance of the same class, the decorator will return the previously created instance.
        - It supports the creation of multiple instances of the same class with different arguments and keyword arguments.
        - This decorator works for multiple classes.

    Usage:
        >>> from decorators import singleton
        >>>
        >>> @singleton
        ... class A:
        ...     def __init__(self, *args, **kwargs):
        ...         pass
        ...
        >>>
        >>> a = A(name='Siddhesh')
        >>> b = A(name='Siddhesh', lname='Sathe')
        >>> c = A(name='Siddhesh', lname='Sathe')
        >>> a is b  # should return False
        False
        >>> b is c  # should return True
        True
        >>>

    Credits:
        This decorator is available at github/siddheshsathe/handy-decorators.
    """

    previous_instances = {}

    @functools.wraps(cls)
    def wrapper(*args, **kwargs):
        if cls in previous_instances and previous_instances.get(cls, None).get("args") == (args, kwargs):
            return previous_instances[cls].get("instance")
        else:
            previous_instances[cls] = {"args": (args, kwargs), "instance": cls(*args, **kwargs)}
            return previous_instances[cls].get("instance")

    return wrapper


def call_conditions(func):
    """
    Decorator to check if the conditions for a function are met before executing it.

    Args:
        func (callable): The function to be decorated.

    Returns:
        callable: The wrapped function.

    Example:
        @condition_check
        def my_function(arg1, arg2):
            # Function implementation

        # Call the decorated function
        my_function("value1", "value2")
    """

    def wrapper(*args, **kwargs):
        function = f"{func.__name__}"
        if not CallCondition.conditions(function=function, *args, **kwargs):
            module_fn = f"{func.__module__}.{func.__name__}"
            io_log.stdout(f"Call conditions for '{module_fn}', not met", level="debug", print_allowed=False)
            return None
        return func(*args, **kwargs)

    return wrapper


def thread_safe_log(func):
    lock = threading.Lock()

    def wrapper_log(cls, *args, **kwargs):
        with lock:
            return func(cls, *args, **kwargs)

    return wrapper_log


class CallCondition:
    @staticmethod
    def all_conditions_met(conditions: list[bool]) -> bool:
        if all(condition for condition in conditions):
            return True
        return False

    @staticmethod
    def conditions(cls: Union["core.SubsearchCore", "core.Initializer"], *args, **kwargs) -> bool:
        if not cls.file_exist:
            return False
        function = kwargs["function"]
        conditions = {
            "opensubtitles": [
                not cls.app_config.foreign_only,
                io_json.check_language_compatibility("opensubtitles"),
                cls.app_config.providers["opensubtitles_hash"] or cls.app_config.providers["opensubtitles_site"],
            ],
            "subscene": [
                io_json.check_language_compatibility("subscene"),
                cls.app_config.providers["subscene_site"],
            ],
            "yifysubtitles": [
                not cls.app_config.foreign_only,
                io_json.check_language_compatibility("yifysubtitles"),
                not cls.release_data.tvseries,
                not cls.provider_urls.yifysubtitles == "",
                cls.app_config.providers["yifysubtitles_site"],
            ],
            "download_files": [len(cls.accepted_subtitles) >= 1],
            "manual_download": [
                len(cls.accepted_subtitles) == 0,
                len(cls.rejected_subtitles) >= 1,
                cls.app_config.manual_download_on_fail,
            ],
            "extract_files": [len(cls.accepted_subtitles) >= 1],
            "autoload_rename": [cls.app_config.autoload_rename, cls.subtitles_found > 1],
            "autoload_move": [cls.app_config.autoload_move, cls.subtitles_found > 1],
            "summary_toast": [cls.app_config.toast_summary],
            "clean_up": [],
        }
        return CallCondition.all_conditions_met(conditions[function])


enable_system_tray: bool


def system_tray_conditions(func):
    def wrapper(*args, **kwargs):
        if enable_system_tray:
            return func(*args, **kwargs)
        else:
            ...

    return wrapper
