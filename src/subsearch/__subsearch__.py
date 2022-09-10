import ctypes
import os
import time

from subsearch.data import __version__, __video__
from subsearch.gui import widget_menu
from subsearch.providers import opensubtitles, subscene
from subsearch.utils import (
    current_user,
    file_manager,
    log,
    raw_config,
    raw_registry,
    string_parser,
)


class BaseInitializer:
    def __init__(self):
        self.current_language = raw_config.get_config_key("current_language")
        self.languages = raw_config.get_config_key("languages")
        self.percentage = raw_config.get_config_key("percentage")
        self.rename_best_match = raw_config.get_config_key("rename_best_match")
        self.show_download_window = raw_config.get_config_key("show_download_window")
        self.show_terminal = raw_config.get_config_key("show_terminal")
        subtitle_type = raw_config.get_config_key("subtitle_type")
        self.hearing_impaired = subtitle_type["hearing_impaired"]
        self.non_hearing_impaired = subtitle_type["non_hearing_impaired"]
        providers = raw_config.get_config_key("providers")
        self.pro_subscene = providers["subscene_site"]
        self.pro_opensubtitles_rss = providers["opensubtitles_rss"]
        self.pro_opensubtitles_hash = providers["opensubtitles_hash"]
        self.file_exist = True if __video__.name is not None else False
        self.file_hash = file_manager.get_hash(__video__.path)
        self.user_parameters = raw_config.UserParameters(
            current_language=self.current_language,
            languages=self.languages,
            hearing_impaired=self.hearing_impaired,
            non_hearing_impaired=self.non_hearing_impaired,
            percentage=self.percentage,
            show_download_window=self.show_download_window,
        )
        self.opensubtitles_hash_results = None
        self.opensubtitles_rss_results = None
        self.subscene_results = None
        self.opensubtitles_sorted_list = []
        self.subscene_sorted_list = []
        self.combined_sorted_list = []
        self.opensubtitles_hash_downloads = 0
        self.opensubtitles_rss_downloads = 0
        self.subscene_downloads = 0
        self.ran_download_tab = False
        if self.file_exist:
            self.file_hash = file_manager.get_hash(__video__.path)
            self.parameters = string_parser.get_parameters(__video__.name, self.file_hash, self.user_parameters)
            log.parameters(self.parameters, self.user_parameters)


class Steps(BaseInitializer):
    def __init__(self):
        self.start = time.perf_counter()
        BaseInitializer.__init__(self)
        ctypes.windll.kernel32.SetConsoleTitleW(f"subsearch - {__version__}")
        if current_user.got_key() is False:
            raw_config.set_default_json()
            raw_registry.add_context_menu()
        if __video__.tmp_directory is not None:
            if not os.path.exists(__video__.tmp_directory):
                os.mkdir(__video__.tmp_directory)
            if not os.path.exists(__video__.subs_directory):
                os.mkdir(__video__.subs_directory)
        if self.file_exist is False:
            widget_menu.open_tab("search")
            return None

        if " " in __video__.name:
            log.output("[Warning: Filename contains spaces]")

    def _provider_opensubtitles(self):
        if self.file_exist is False:
            return None
        if self.languages[self.current_language] == "N/A":
            log.output("\n[Searching on opensubtitles]")
            log.output(f"{self.current_language} not supported on opensubtitles\n")
            return None

        _opensubtitles = opensubtitles.OpenSubtitles(self.parameters, self.user_parameters)
        if self.pro_opensubtitles_hash and self.file_hash is not None:
            log.output("\n[Searching on opensubtitles - hash]")
            self.opensubtitles_hash = _opensubtitles.parse_hash()
        if self.pro_opensubtitles_rss:
            log.output("\n[Searching on opensubtitles - rss]")
            self.opensubtitles_rss = _opensubtitles.parse_rss()

        self.opensubtitles_sorted_list = _opensubtitles.sorted_list()

    def _provider_subscene(self):
        if self.file_exist is False:
            return None
        if self.pro_subscene is False:
            return None
        log.output("\n[Searching on subscene - title]")
        _subscene = subscene.Subscene(self.parameters, self.user_parameters)
        self.subscene = _subscene.parse()
        self.subscene_sorted_list = _subscene.sorted_list()

    def _download_files(self):
        if self.file_exist is False:
            return None
        if self.pro_opensubtitles_hash and self.opensubtitles_hash is not None:
            log.output("\n[Downloading from opensubtitles - hash]")
            for item in self.opensubtitles_hash:
                self.opensubtitles_hash_downloads = file_manager.download_subtitle(item)
                log.output("Done with tasks")
                log.output("\n")
        if self.pro_opensubtitles_rss and self.opensubtitles_rss is not None:
            log.output("\n[Downloading from opensubtitles - rss]")
            for item in self.opensubtitles_rss:
                self.opensubtitles_rss_downloads = file_manager.download_subtitle(item)
                log.output("Done with tasks")
        if self.pro_subscene and self.subscene is not None:
            log.output("\n[Downloading from subscene]")
            for item in self.subscene:
                self.subscene_downloads = file_manager.download_subtitle(item)
                log.output("Done with tasks")

    def _not_downloaded(self):
        if self.file_exist is False:
            return None
        total_dls = self.opensubtitles_hash_downloads + self.opensubtitles_rss_downloads + self.subscene_downloads
        if self.show_download_window and total_dls == 0:
            self.combined_sorted_list = list(self.opensubtitles_sorted_list)
            self.combined_sorted_list.extend(x for x in self.subscene_sorted_list if x not in self.combined_sorted_list)
            self.combined_sorted_list.sort(key=lambda x: x[0], reverse=True)
        if len(self.combined_sorted_list) > 0:
            file_manager.write_not_downloaded_tmp(__video__.tmp_directory, self.combined_sorted_list)
            widget_menu.open_tab("download")
            self.ran_download_tab = True

    def _extract_zip_files(self):
        if self.file_exist is False:
            return None
        if self.ran_download_tab:
            return None
        log.output("\n[Proccessing downloads]")
        file_manager.extract_files(__video__.tmp_directory, __video__.subs_directory, ".zip")

    def _clean_up(self):
        if self.file_exist is False:
            return None
        if self.rename_best_match:
            file_manager.rename_best_match(f"{self.parameters.release}.srt", __video__.directory, ".srt")
        log.output("\n[Cleaning up]")
        file_manager.clean_up_files(__video__.subs_directory, "nfo")
        file_manager.del_directory(__video__.tmp_directory)
        log.output("Done with tasks")

    def _pre_exit(self):
        elapsed = time.perf_counter() - self.start
        log.output(f"\nFinished in {elapsed} seconds")

        if self.show_terminal and current_user.check_is_exe() is False:
            try:
                input("Ctrl + c or Enter to exit")
            except KeyboardInterrupt:
                pass
