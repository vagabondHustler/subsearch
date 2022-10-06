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
        self.user_data = raw_config.get_user_data()
        if __video__ is not None:
            self.file_exist = True
            self.file_hash = file_manager.get_hash(__video__.path)
        else:
            self.file_exist = False
            self.file_hash = "000000000000000000"
        self.results: dict[str, list[DownloadData]] = {}
        self.skipped: dict[str, list[FormattedData]] = {}
        self.skipped_combined: list[FormattedData] = []
        self.downloads: dict[str, int] = {}

        for k in self.user_data.providers.keys():
            self.results[k] = []
            self.skipped[k] = []
            self.downloads[k] = 0

        self.ran_download_tab = False
        if self.file_exist:
            self.release_data = string_parser.get_file_search_data(__video__.name, self.file_hash)
            self.provider_data = string_parser.get_provider_urls(self.file_hash, self.user_data, self.release_data)
            log.set_logger_data(self.release_data, self.user_data, self.provider_data)
            log.output_parameters()

    def all_providers_disabled(self) -> bool:
        self.user_data = raw_config.get_user_data()
        if (
            self.user_data.providers["subscene_site"] is False
            and self.user_data.providers["opensubtitles_site"] is False
            and self.user_data.providers["opensubtitles_hash"] is False
            and self.user_data.providers["yifysubtitles_site"] is False
        ):
            return True
        return False

    def download_results(self, results: list[DownloadData]) -> int:
        for i in results:
            downloads = file_manager.download_subtitle(i)
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
            log.output_skip_provider("opensubtitles", f"{self.user_data.current_language} not supported on opensubtitles")
            return None
        if (
            self.user_data.providers["opensubtitles_hash"] is False
            and self.user_data.providers["opensubtitles_site"] is False
        ):
            return None
        log.output_header("Searching on opensubtitles")
        _opensubs = opensubtitles.OpenSubtitles(self.release_data, self.user_data, self.provider_data)
        if self.user_data.providers["opensubtitles_hash"] and self.file_hash != "000000000000000000":
            self.results["opensubtitles_hash"] = _opensubs.parse_hash_results()
        if self.user_data.providers["opensubtitles_site"]:
            self.results["opensubtitles_site"] = _opensubs.parse_site_results()
        self.skipped["opensubtitles_site"] = _opensubs._sorted_list()

    def _provider_subscene(self) -> None:
        if self.file_exist is False:
            return None
        if self.user_data.providers["subscene_site"] is False:
            return None
        log.output_header("Searching on subscene")
        _subscene = subscene.Subscene(self.release_data, self.user_data, self.provider_data)
        self.results["subscene_site"] = _subscene.parse_site_results()
        self.skipped["subscene_site"] = _subscene._sorted_list()

    def _provider_yifysubtitles(self) -> None:
        if self.file_exist is False:
            return None
        if self.release_data.series:
            log.output_skip_provider("yifysubtitles", "Yifysubtitles only host subtitles for movies")
            return None
        if self.provider_data.yifysubtitles == "N/A":
            log.output_skip_provider("yifysubtitles", f"{self.user_data.current_language} not supported on yifysubtitles")
            return None
        if self.user_data.providers["yifysubtitles_site"]:
            log.output_header("Searching on yifysubtitles")
            _yifysubs = yifysubtitles.YifiSubtitles(self.release_data, self.user_data, self.provider_data)
            self.results["yifysubtitles_site"] = _yifysubs.parse_site_results()
            self.skipped["yifysubtitles_site"] = _yifysubs._sorted_list()

    def _download_files(self) -> None:
        if self.file_exist is False:
            return None
        if not any(self.results.values()):
            return None
        log.output_header(f"Downloading subtitles")
        for provider, data in self.results.items():
            if self.user_data.providers[provider] is False:
                continue
            if not data:
                continue
            self.downloads[provider] = self.download_results(data)
        log.output_done_with_tasks(end_new_line=True)

    def _not_downloaded(self) -> None:
        if self.file_exist is False:
            return None

        number_of_downloads = sum(v for v in self.downloads.values())
        if self.user_data.show_download_window and number_of_downloads > 0:
            return None

        for data_list in self.skipped.values():
            if not data_list:
                continue
            for data in data_list:
                self.skipped_combined.append(data)

        if self.skipped_combined:
            widget_menu.open_tab("download", formatted_data=self.skipped_combined)
            self.ran_download_tab = True
        log.output_done_with_tasks(end_new_line=True)

    def _extract_zip_files(self) -> None:
        if self.file_exist is False:
            return None
        if self.ran_download_tab:
            return None
        if self.all_providers_disabled():
            return None

        log.output_header("Extracting downloads")
        file_manager.extract_files(__video__.tmp_directory, __video__.subs_directory, ".zip")
        log.output_done_with_tasks(end_new_line=True)

    def _clean_up(self) -> None:
        if self.file_exist is False:
            return None
        if self.user_data.rename_best_match:
            log.output_header("Renaming best match")
            file_manager.rename_best_match(f"{self.release_data.release}.srt", __video__.directory, ".srt")
            log.output_done_with_tasks(end_new_line=True)

        log.output_header("Cleaning up")
        file_manager.clean_up_files(__video__.subs_directory, "nfo")
        file_manager.del_directory(__video__.tmp_directory)
        log.output_done_with_tasks(end_new_line=True)

    def _pre_exit(self) -> None:
        elapsed = time.perf_counter() - self.start
        log.output(f"Finished in {elapsed} seconds")

        if self.user_data.show_terminal is False:
            return None
        if current_user.running_from_exe():
            return None

        try:
            input("Ctrl + c or Enter to exit")
        except KeyboardInterrupt:
            pass
