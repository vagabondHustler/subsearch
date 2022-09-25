import ctypes
import time

from subsearch.data import __version__, __video__
from subsearch.data.data_fields import DownloadData, FormattedData
from subsearch.gui import widget_menu
from subsearch.providers import opensubtitles, subscene, yifysubtitles
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
        self.log = log.SubsearchOutputs()
        self.user_config_data = raw_config.get_user_data()
        if __video__ is not None:
            self.file_exist = True
            self.file_hash = file_manager.get_hash(__video__.path)
        else:
            self.file_exist = False
            self.file_hash = "000000000000000000"
        self.opensubtitles_hash_results = None
        self.opensubtitles_site_results = None
        self.subscene_results = None
        self.yifysubtitles_results = None
        self.opensubtitles_fd: list = []
        self.subscene_fd: list = []
        self.yifysubtitles_fd: list = []
        self.combined_fd: list[FormattedData] = []
        self.opensubtitles_hash_dls = 0
        self.opensubtitles_site_dls = 0
        self.subscene_dls = 0
        self.yifysubtitles_dls = 0
        self.ran_download_tab = False
        if self.file_exist:
            self.file_hash = file_manager.get_hash(__video__.path)
            self.file_search_data = string_parser.get_file_search_data(__video__.name, self.file_hash)
            self.provider_url_data = string_parser.get_provider_urls(
                self.file_hash, self.user_config_data, self.file_search_data
            )
            self.log.app_parameters(self.file_search_data, self.user_config_data, self.provider_url_data)

    def all_providers_disabled(self) -> bool:
        self.user_config_data = raw_config.get_user_data()
        if (
            self.user_config_data.providers["subscene_site"] is False
            and self.user_config_data.providers["opensubtitles_site"] is False
            and self.user_config_data.providers["opensubtitles_hash"] is False
            and self.user_config_data.providers["yifysubtitles_site"] is False
        ):
            return True
        return False

    def download_results(self, provider: str, results: list[DownloadData]) -> int:
        log.output(f"[Downloading from {provider}]")
        for i in results:
            downloads = file_manager.download_subtitle(i)
        self.log.done_with_tasks(end_new_line=True)
        return downloads


class Steps(BaseInitializer):
    def __init__(self) -> None:
        self.start = time.perf_counter()
        BaseInitializer.__init__(self)
        ctypes.windll.kernel32.SetConsoleTitleW(f"subsearch - {__version__}")
        if current_user.registry_key_exists() is False:
            raw_config.set_default_json()
            raw_registry.add_context_menu()
        file_manager.make_necessary_directories()
        if self.file_exist is False:
            widget_menu.open_tab("search")
            return None

        if " " in __video__.name:
            log.warning_spaces_in_filename()

    def _provider_opensubtitles(self) -> None:
        if self.file_exist is False:
            return None
        if self.user_data.language_code3 == "N/A":
            log.output_skipping_provider(
                "opensubtitles", f"{self.user_data.current_language} not supported on opensubtitles"
            )
            return None

        _opensubtitles = opensubtitles.OpenSubtitles(self.file_search_data, self.user_config_data, self.provider_url_data)
        if self.user_config_data.providers["opensubtitles_hash"] and self.file_hash != "000000000000000000":
            log.output("[Searching on opensubtitles - hash]")
            self.opensubtitles_hash_results = _opensubtitles.parse_hash_results()
        if self.user_config_data.providers["opensubtitles_site"]:
            log.output("[Searching on opensubtitles - site]")
            self.opensubtitles_site_results = _opensubtitles.parse_site_results()
        self.opensubtitles_fd = _opensubtitles._sorted_list()

    def _provider_subscene(self) -> None:
        if self.file_exist is False:
            return None
        if self.user_config_data.providers["subscene_site"] is False:
            return None
        log.output("[Searching on subscene - title]")
        _subscene = subscene.Subscene(self.file_search_data, self.user_config_data, self.provider_url_data)
        self.subscene_results = _subscene.parse_site_results()
        self.subscene_fd = _subscene._sorted_list()

    def _provider_yifysubtitles(self) -> None:
        if self.file_exist is False:
            return None
        if self.file_search_data.series or self.provider_url_data.yifysubtitles == "N/A":
            self.log.skip_provider("yifysubtitles", "yifysubtitles only host subtitles for movies")
            return None
        if self.user_config_data.providers["yifysubtitles_site"]:
            log.output("[Searching on yifysubtitles - subtitle]")
            _yifysubtitles = yifysubtitles.YifiSubtitles(
                self.file_search_data, self.user_config_data, self.provider_url_data
            )
            self.yifysubtitles_results = _yifysubtitles.parse_site_results()
            self.subscene_fd = _yifysubtitles._sorted_list()

    def _download_files(self) -> None:
        if self.file_exist is False:
            return None

        if self.user_config_data.providers["opensubtitles_hash"] and self.opensubtitles_hash_results is not None:
            self.opensubtitles_hash_dls = self.download_results("opensubtitles - hash", self.opensubtitles_hash_results)

        if self.user_config_data.providers["opensubtitles_site"] and self.opensubtitles_site_results is not None:
            self.opensubtitles_site_dls = self.download_results("opensubtitles - site", self.opensubtitles_site_results)

        if self.user_config_data.providers["subscene_site"] and self.subscene_results is not None:
            self.subscene_dls = self.download_results("subscene", self.subscene_results)

        if self.user_config_data.providers["yifysubtitles_site"] and self.yifysubtitles_results is not None:
            self.yifysubtitles_dls = self.download_results("yifysubtitles", self.yifysubtitles_results)

    def _not_downloaded(self) -> None:
        if self.file_exist is False:
            return None
        total_dls = self.opensubtitles_hash_dls + self.opensubtitles_site_dls + self.subscene_dls + self.yifysubtitles_dls
        if self.user_config_data.show_download_window and total_dls == 0:
            self.combined_fd: list[FormattedData] = self.opensubtitles_fd + self.subscene_fd + self.yifysubtitles_fd
        if self.combined_fd:
            widget_menu.open_tab("download", formatted_data=self.combined_fd)
            self.ran_download_tab = True

    def _extract_zip_files(self) -> None:
        if self.file_exist is False:
            return None
        if self.ran_download_tab:
            return None
        if self.all_providers_disabled():
            return None
        log.output("[Extracting downloads]")
        file_manager.extract_files(__video__.tmp_directory, __video__.subs_directory, ".zip")
        self.log.done_with_tasks(end_new_line=True)

    def _clean_up(self) -> None:
        if self.file_exist is False:
            return None
        if self.user_config_data.rename_best_match:
            log.output("[Renaming best match]")
            file_manager.rename_best_match(f"{self.file_search_data.release}.srt", __video__.directory, ".srt")
            self.log.done_with_tasks(end_new_line=True)
        log.output("[Cleaning up]")
        file_manager.clean_up_files(__video__.subs_directory, "nfo")
        file_manager.del_directory(__video__.tmp_directory)
        self.log.done_with_tasks(end_new_line=True)

    def _pre_exit(self) -> None:
        elapsed = time.perf_counter() - self.start
        log.output(f"Finished in {elapsed} seconds")

        if self.user_config_data.show_terminal and current_user.running_from_exe() is False:
            try:
                input("Ctrl + c or Enter to exit")
            except KeyboardInterrupt:
                pass
