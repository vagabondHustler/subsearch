import ctypes
from typing import Any, Callable, Union

from subsearch import core
from subsearch.globals import exceptions
from subsearch.globals.constants import FILE_PATHS
from subsearch.data import __guid__
from subsearch.utils import io_log, io_toml


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
        if not _CoreSubsearchFuncCondtitons.conditions_met(func_name=func_name, *args, **kwargs):
            module_func = f"{func.__module__}.{func.__name__}"
            io_log.stdout(f"Call conditions for '{module_func}', not met", level="debug", print_allowed=False)
            return None
        return func(*args, **kwargs)

    return wrapper


class _CoreSubsearchFuncCondtitons:
    @staticmethod
    def language_compatibility(provider: str) -> bool:
        language = io_toml.load_toml_value(FILE_PATHS.config, "subtitle_filters.language")
        incompatibility: list[str] = io_toml.load_toml_value(FILE_PATHS.language_data, f"{language}.incompatibility")
        if provider in incompatibility:
            return False
        return True

    @staticmethod
    def eval_all_true(conditions: list[bool]) -> bool:
        if False in conditions:
            return False
        return True

    @staticmethod
    def conditions_met(cls: Union["core.SubsearchCore", "core.Initializer"], *args, **kwargs) -> bool:
        if not cls.file_exist:
            return False
        func_name = kwargs["func_name"]
        conditions: dict[str, list[bool]] = {
            "opensubtitles": [
                _CoreSubsearchFuncCondtitons.language_compatibility("opensubtitles"),
                cls.app_config.providers["opensubtitles_hash"] or cls.app_config.providers["opensubtitles_site"],
            ],
            "subscene": [
                _CoreSubsearchFuncCondtitons.language_compatibility("subscene"),
                cls.app_config.providers["subscene_site"],
            ],
            "yifysubtitles": [
                not cls.app_config.only_foreign_parts,
                _CoreSubsearchFuncCondtitons.language_compatibility("yifysubtitles"),
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
            "subtitle_rename": [cls.app_config.subtitle_post_processing["rename"], cls.subtitles_found >= 1],
            "subtitle_move_best": [
                cls.app_config.subtitle_post_processing["move_best"],
                cls.subtitles_found >= 1,
                not cls.app_config.subtitle_post_processing["move_all"],
            ],
            "subtitle_move_all": [cls.app_config.subtitle_post_processing["move_all"], cls.subtitles_found > 1],
            "summary_notification": [cls.app_config.summary_notification],
            "clean_up": [],
        }
        return _CoreSubsearchFuncCondtitons.eval_all_true(conditions[func_name])


enable_system_tray: bool


def system_tray_conditions(func) -> Callable:
    def wrapper(*args, **kwargs) -> Any:
        if enable_system_tray:
            return func(*args, **kwargs)

    return wrapper
