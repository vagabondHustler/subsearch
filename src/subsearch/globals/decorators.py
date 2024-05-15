import ctypes
import sys
from typing import Any, Callable, Union

from subsearch import core
from subsearch.globals import exceptions
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
        if not _CoreSubsearchFuncCondtitons.conditions_met(func_name=func_name, *args, **kwargs):
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

        cfg = cls.app_config
        acc_subs = cls.accepted_subtitles
        rej_subs = cls.rejected_subtitles

        df_senario_1 = not cfg.always_open and not cfg.no_automatic_downloads
        df_senario_2 = cfg.always_open and not cfg.no_automatic_downloads

        open_dm_senario_1 = len(acc_subs) == 0 and len(rej_subs) >= 1 and cfg.open_on_no_matches
        open_dm_senario_2 = len(acc_subs) >= 1 and cfg.always_open and cfg.no_automatic_downloads
        open_dm_senario_3 = len(rej_subs) >= 1 and cfg.always_open

        func_name = kwargs["func_name"]
        conditions: dict[str, list[bool]] = {
            "init_search": [],
            "opensubtitles": [
                _CoreSubsearchFuncCondtitons.language_compatibility("opensubtitles"),
                cfg.providers["opensubtitles_hash"] or cfg.providers["opensubtitles_site"],
            ],
            "yifysubtitles": [
                not cfg.only_foreign_parts,
                _CoreSubsearchFuncCondtitons.language_compatibility("yifysubtitles"),
                not cls.release_data.tvseries,
                not cls.provider_urls.yifysubtitles == "",
                cfg.providers["yifysubtitles_site"],
            ],
            "download_files": [
                len(cls.accepted_subtitles) >= 1,
                (df_senario_1 or df_senario_2),
            ],
            "download_manager": [(open_dm_senario_1 or open_dm_senario_2 or open_dm_senario_3)],
            "extract_files": [len(cls.accepted_subtitles) >= 1],
            "subtitle_post_processing": [],
            "subtitle_rename": [cfg.subtitle_post_processing["rename"], cls.downloaded_subtitles >= 1],
            "subtitle_move_best": [
                cfg.subtitle_post_processing["move_best"],
                cls.downloaded_subtitles >= 1,
                not cfg.subtitle_post_processing["move_all"],
            ],
            "subtitle_move_all": [cfg.subtitle_post_processing["move_all"], cls.downloaded_subtitles > 1],
            "summary_notification": [cfg.summary_notification],
            "clean_up": [],
        }
        return _CoreSubsearchFuncCondtitons.eval_all_true(conditions[func_name])


def system_tray_conditions(func) -> Callable:
    def wrapper(*args, **kwargs) -> Any:
        if enable_system_tray:
            return func(*args, **kwargs)

    return wrapper


def except_hook(func, excepthook_) -> Callable:
    def wrapper(*args, **kwargs) -> Any:
        sys.excepthook = excepthook_
        return func(*args, **kwargs)

    return wrapper
