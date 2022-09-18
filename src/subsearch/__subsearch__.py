import ctypes
import os
import time

from subsearch.data import __version__, __video__
from subsearch.gui import widget_menu
from subsearch.providers import opensubtitles, subscene, yifysubtitles
from subsearch.providers.generic import FormattedData
from subsearch.utils import (
    current_user,
    file_manager,
    log,
    raw_config,
    raw_registry,
    string_parser,
)


class BaseInitializer:
    def __init__(self) -> None:
        self.current_language = raw_config.get_config_key("current_language")
        self.languages = raw_config.get_config_key("languages")
        self.percentage = raw_config.get_config_key("percentage")
        self.rename_best_match = raw_config.get_config_key("rename_best_match")
        self.show_download_window = raw_config.get_config_key("show_download_window")
        self.show_terminal = raw_config.get_config_key("show_terminal")
        subtitle_type = raw_config.get_config_key("subtitle_type")
        self.hearing_impaired = subtitle_type["hearing_impaired"]
        self.non_hearing_impaired = subtitle_type["non_hearing_impaired"]
        self.providers = raw_config.get_config_key("providers")
        self.pro_subscene = self.providers["subscene_site"]
        self.pro_opensubtitles_rss = self.providers["opensubtitles_rss"]
        self.pro_opensubtitles_hash = self.providers["opensubtitles_hash"]
        self.pro_yifysubtitles = self.providers["yifysubtitles_site"]
        self.file_exist = True if __video__.name != "N/A" else False
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
        self.yifysubtitles_results = None
        self.opensubtitles_sorted_list: list = []
        self.subscene_sorted_list: list = []
        self.yifysubtitles_sorted_list: list = []
        self.combined_list: list[FormattedData] = []
        self.opensubtitles_hash_downloads = 0
        self.opensubtitles_rss_downloads = 0
        self.subscene_downloads = 0
        self.yifysubtitles_downloads = 0
        self.ran_download_tab = False
        if self.file_exist:
            self.file_hash = file_manager.get_hash(__video__.path)
            self.parameters = string_parser.get_parameters(__video__.name, self.file_hash, self.user_parameters)
            log.parameters(self.parameters, self.user_parameters)

    def all_providers_disabled(self) -> bool:
        self.providers = raw_config.get_config_key("providers")
        if (
            self.pro_subscene is False
            and self.pro_opensubtitles_rss is False
            and self.pro_opensubtitles_hash is False
            and self.pro_yifysubtitles is False
        ):
            return True
        return False


class Steps(BaseInitializer):
    def __init__(self) -> None:
        self.start = time.perf_counter()
        BaseInitializer.__init__(self)
        ctypes.windll.kernel32.SetConsoleTitleW(f"subsearch - {__version__}")
        if current_user.got_key() is False:
            raw_config.set_default_json()
            raw_registry.add_context_menu()
        if __video__.tmp_directory != "N/A":
            if not os.path.exists(__video__.tmp_directory):
                os.mkdir(__video__.tmp_directory)
            if not os.path.exists(__video__.subs_directory):
                os.mkdir(__video__.subs_directory)
        if self.file_exist is False:
            widget_menu.open_tab("search")
            return None

        if " " in __video__.name:
            log.output("[Warning: Filename contains spaces]")

    def _provider_opensubtitles(self) -> None:
        if self.file_exist is False:
            return None
        if self.languages[self.current_language] == "N/A":
            log.output("\n[Searching on opensubtitles]")
            log.output(f"{self.current_language} not supported on opensubtitles\n")
            return None

        _opensubtitles = opensubtitles.OpenSubtitles(self.parameters, self.user_parameters)
        if self.pro_opensubtitles_hash and self.file_hash != "000000000000000000":
            log.output("\n[Searching on opensubtitles - hash]")
            self.opensubtitles_hash_results = _opensubtitles.parse_hash_results()
        if self.pro_opensubtitles_rss:
            log.output("\n[Searching on opensubtitles - rss]")
            self.opensubtitles_rss_results = _opensubtitles.parse_site_results()
        self.opensubtitles_sorted_list = _opensubtitles._sorted_list()

    def _provider_subscene(self) -> None:
        if self.file_exist is False:
            return None
        if self.pro_subscene is False:
            return None
        log.output("\n[Searching on subscene - title]")
        _subscene = subscene.Subscene(self.parameters, self.user_parameters)
        self.subscene_results = _subscene.parse_site_results()
        self.subscene_sorted_list = _subscene._sorted_list()

    def _provider_yifysubtitles(self) -> None:
        if self.file_exist is False:
            return None
        if self.parameters.series or self.parameters.url_yifysubtitles == "N/A":
            log.output("\n[Searching on yifysubtitles - subtitle]]")
            log.output("yifysubtitles only have subtitles for movies")
            log.output("Done with tasks")
            log.output("\n")
            return None
        if self.pro_yifysubtitles:
            log.output("\n[Searching on yifysubtitles - subtitle]")
            _yifysubtitles = yifysubtitles.YifiSubtitles(self.parameters, self.user_parameters)
            self.yifysubtitles_results = _yifysubtitles.parse_site_results()
            self.subscene_sorted_list = _yifysubtitles._sorted_list()

    def _download_files(self) -> None:
        if self.file_exist is False:
            return None
        if self.pro_opensubtitles_hash and self.opensubtitles_hash_results is not None:
            log.output("\n[Downloading from opensubtitles - hash]")
            for item in self.opensubtitles_hash_results:
                self.opensubtitles_hash_downloads = file_manager.download_subtitle(item)
                log.output("Done with tasks")
                log.output("\n")
        if self.pro_opensubtitles_rss and self.opensubtitles_rss_results is not None:
            log.output("\n[Downloading from opensubtitles - rss]")
            for item in self.opensubtitles_rss_results:
                self.opensubtitles_rss_downloads = file_manager.download_subtitle(item)
                log.output("Done with tasks")
        if self.pro_subscene and self.subscene_results is not None:
            log.output("\n[Downloading from subscene]")
            for item in self.subscene_results:
                self.subscene_downloads = file_manager.download_subtitle(item)
                log.output("Done with tasks")
        if self.pro_yifysubtitles and self.yifysubtitles_results is not None:
            log.output("\n[Downloading from yifysubtitles]")
            for item in self.yifysubtitles_results:
                self.yifysubtitles_downloads = file_manager.download_subtitle(item)
                log.output("Done with tasks")

    def _not_downloaded(self) -> None:
        if self.file_exist is False:
            return None
        total_dls = (
            self.opensubtitles_hash_downloads
            + self.opensubtitles_rss_downloads
            + self.subscene_downloads
            + self.yifysubtitles_downloads
        )
        if self.show_download_window and total_dls == 0:
            self.combined_list: list[FormattedData] = (
                self.opensubtitles_sorted_list + self.subscene_sorted_list + self.yifysubtitles_sorted_list
            )
        if len(self.combined_list) > 0:
            widget_menu.open_tab("download", formatted_data=self.combined_list)
            self.ran_download_tab = True

    def _extract_zip_files(self) -> None:
        if self.file_exist is False:
            return None
        if self.ran_download_tab:
            return None
        if self.all_providers_disabled():
            return None
        log.output("\n[Proccessing downloads]")
        file_manager.extract_files(__video__.tmp_directory, __video__.subs_directory, ".zip")

    def _clean_up(self) -> None:
        if self.file_exist is False:
            return None
        if self.rename_best_match:
            file_manager.rename_best_match(f"{self.parameters.release}.srt", __video__.directory, ".srt")
        log.output("\n[Cleaning up]")
        file_manager.clean_up_files(__video__.subs_directory, "nfo")
        file_manager.del_directory(__video__.tmp_directory)
        log.output("Done with tasks")

    def _pre_exit(self) -> None:
        elapsed = time.perf_counter() - self.start
        log.output(f"\nFinished in {elapsed} seconds")

        if self.show_terminal and current_user.check_is_exe() is False:
            try:
                input("Ctrl + c or Enter to exit")
            except KeyboardInterrupt:
                pass
