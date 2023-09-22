import ctypes
import functools
import threading
from typing import Any, Callable, Union

from subsearch import core
from subsearch.data import __guid__
from subsearch.data.constants import FILE_PATHS
from subsearch.utils import exceptions, io_log, io_toml


def apply_mutex(func: Callable) -> Callable:
    def inner(*args, **kwargs):
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


def check_option_disabled(func):
    def wrapper(self, event, *args, **kwargs):
        btn = event.widget
        if btn.instate(["disabled"]):
            return None
        return func(self, event, *args, **kwargs)

    return wrapper


def singleton(cls):
    previous_instances: dict[Callable, Any] = {}

    @functools.wraps(cls)
    def wrapper(*args, **kwargs):
        if cls in previous_instances and previous_instances.get(cls, None).get("args") == (args, kwargs):
            return previous_instances[cls].get("instance")
        else:
            previous_instances[cls] = {"args": (args, kwargs), "instance": cls(*args, **kwargs)}
            return previous_instances[cls].get("instance")

    return wrapper


def call_conditions(func):
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
    def language_compatibility(provider: str):
        language = io_toml.load_toml_value(FILE_PATHS.config, "subtitle_filters.language")
        incompatibility: list[str] = io_toml.load_toml_value(FILE_PATHS.language_data, f"{language}.incompatibility")
        if provider in incompatibility:
            return False
        return True

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
                CallCondition.language_compatibility("opensubtitles"),
                cls.app_config.providers["opensubtitles_hash"] or cls.app_config.providers["opensubtitles_site"],
            ],
            "subscene": [
                CallCondition.language_compatibility("subscene"),
                cls.app_config.providers["subscene_site"],
            ],
            "yifysubtitles": [
                not cls.app_config.only_foreign_parts,
                CallCondition.language_compatibility("yifysubtitles"),
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
            "subtitle_post_processing": [],
            "subtitle_rename": [cls.app_config.subtitle_post_processing["rename"], cls.subtitles_found > 1],
            "subtitle_move_best": [
                cls.app_config.subtitle_post_processing["move_best"],
                cls.subtitles_found > 1,
                not cls.app_config.subtitle_post_processing["move_all"],
            ],
            "subtitle_move_all": [cls.app_config.subtitle_post_processing["move_all"], cls.subtitles_found > 1],
            "summary_notification": [cls.app_config.summary_notification],
            "clean_up": [],
        }
        return CallCondition.all_conditions_met(conditions[function])


enable_system_tray: bool


def system_tray_conditions(func):
    def wrapper(*args, **kwargs):
        if enable_system_tray:
            return func(*args, **kwargs)

    return wrapper
