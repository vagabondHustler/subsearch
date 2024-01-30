from typing import Union

from subsearch import core
from subsearch.globals.constants import FILE_PATHS
from subsearch.utils import io_toml


class Singleton(type):
    _instances: dict[type, type] = {}

    def __call__(cls, *args, **kwargs) -> type:
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class SubsearchFuncCondtitons:
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
            "opensubtitles": [
                SubsearchFuncCondtitons.language_compatibility("opensubtitles"),
                cfg.providers["opensubtitles_hash"] or cfg.providers["opensubtitles_site"],
            ],
            "subscene": [
                SubsearchFuncCondtitons.language_compatibility("subscene"),
                cfg.providers["subscene_site"],
            ],
            "yifysubtitles": [
                not cfg.only_foreign_parts,
                SubsearchFuncCondtitons.language_compatibility("yifysubtitles"),
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
        return SubsearchFuncCondtitons.eval_all_true(conditions[func_name])
