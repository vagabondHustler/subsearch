import ctypes
import time

from subsearch.data import __version__, __video__
from subsearch.data.data_objects import DownloadMetaData, FormattedMetadata
from subsearch.gui import widget_menu
from subsearch.providers import opensubtitles, subscene, yifysubtitles
from subsearch.utils import file_manager, log, raw_config, raw_registry, string_parser


class Initializer:
    def __init__(self) -> None:
        self.app_data = raw_config.get_app_config()
        if __video__ is not None:
            self.file_exist = True
            self.file_hash = file_manager.get_hash(__video__.file_path)
        else:
            self.file_exist = False
            self.file_hash = "000000000000000000"
        self.results: dict[str, list[DownloadMetaData]] = {}
        self.skipped: dict[str, list[FormattedMetadata]] = {}
        self.skipped_combined: list[FormattedMetadata] = []
        self.downloads: dict[str, int] = {}

        for provider in self.app_data.providers.keys():
            self.results[provider] = []
            self.skipped[provider] = []
            self.downloads[provider] = 0

        self.ran_download_tab = False
        if self.file_exist:
            self.release_data = string_parser.get_release_metadata(__video__.filename, self.file_hash)
            create_provider_urls = string_parser.CreateProviderUrls(self.file_hash, self.app_data, self.release_data)
            self.provider_urls = create_provider_urls.retrieve_urls()
            log.set_logger_data(self.release_data, self.app_data, self.provider_urls)
            log.output_parameters()

    def all_providers_disabled(self) -> bool:
        self.app_data = raw_config.get_app_config()
        if (
            self.app_data.providers["subscene_site"] is False
            and self.app_data.providers["opensubtitles_site"] is False
            and self.app_data.providers["opensubtitles_hash"] is False
            and self.app_data.providers["yifysubtitles_site"] is False
        ):
            return True
        return False

    def download_results(self, results: list[DownloadMetaData]) -> int:
        for result in results:
            downloads = file_manager.download_subtitle(result)
        return downloads


class AppSteps(Initializer):
    def __init__(self) -> None:
        self.start = time.perf_counter()
        Initializer.__init__(self)
        ctypes.windll.kernel32.SetConsoleTitleW(f"subsearch - {__version__}")
        if raw_registry.registry_key_exists() is False:
            raw_config.set_default_json()
            raw_registry.add_context_menu()
        file_manager.make_necessary_directories()
        if self.file_exist is False:
            widget_menu.open_tab("search")
            return None

        if " " in __video__.filename:
            log.warning_spaces_in_filename()
        log.output_header("Search started")

    def _provider_opensubtitles(self) -> None:
        if self.file_exist is False:
            return None
        if self.app_data.language_iso_639_3 == "N/A":
            return None
        if self.app_data.providers["opensubtitles_hash"] is False and self.app_data.providers["opensubtitles_site"] is False:
            return None
        # log.output_header("Searching on opensubtitles")
        _opensubs = opensubtitles.OpenSubtitles(self.release_data, self.app_data, self.provider_urls)
        if self.app_data.providers["opensubtitles_hash"] and self.file_hash != "000000000000000000":
            self.results["opensubtitles_hash"] = _opensubs.parse_hash_results()
        if self.app_data.providers["opensubtitles_site"]:
            self.results["opensubtitles_site"] = _opensubs.parse_site_results()
        self.skipped["opensubtitles_site"] = _opensubs._sorted_list()

    def _provider_subscene(self) -> None:
        if self.file_exist is False:
            return None
        if self.app_data.providers["subscene_site"] is False:
            return None
        # log.output_header("Searching on subscene")
        _subscene = subscene.Subscene(self.release_data, self.app_data, self.provider_urls)
        self.results["subscene_site"] = _subscene.parse_site_results()
        self.skipped["subscene_site"] = _subscene._sorted_list()

    def _provider_yifysubtitles(self) -> None:
        if self.file_exist is False:
            return None
        if self.release_data.tvseries:
            return None
        if self.provider_urls.yifysubtitles == "N/A":
            return None
        if self.app_data.providers["yifysubtitles_site"]:
            # log.output_header("Searching on yifysubtitles")
            _yifysubs = yifysubtitles.YifiSubtitles(self.release_data, self.app_data, self.provider_urls)
            self.results["yifysubtitles_site"] = _yifysubs.parse_site_results()
            self.skipped["yifysubtitles_site"] = _yifysubs._sorted_list()

    def _download_files(self) -> None:
        if self.file_exist is False:
            return None
        if not any(self.results.values()):
            return None
        log.output_header(f"Downloading subtitles")
        for provider, data in self.results.items():
            if self.app_data.providers[provider] is False:
                continue
            if not data:
                continue
            self.downloads[provider] = self.download_results(data)
        log.output_done_with_tasks(end_new_line=True)

    def _not_downloaded(self) -> None:
        if self.file_exist is False:
            return None

        number_of_downloads = sum(v for v in self.downloads.values())
        if self.app_data.manual_download_tab and number_of_downloads > 0:
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
        if self.app_data.rename_best_match:
            log.output_header("Renaming best match")
            file_manager.rename_best_match(f"{self.release_data.release}.srt", __video__.directory_path, ".srt")
            log.output_done_with_tasks(end_new_line=True)

        log.output_header("Cleaning up")
        file_manager.clean_up_files(__video__.subs_directory, "nfo")
        file_manager.del_directory(__video__.tmp_directory)
        log.output_done_with_tasks(end_new_line=True)

    def _pre_exit(self) -> None:
        elapsed = time.perf_counter() - self.start
        log.output(f"Finished in {elapsed} seconds")

        if self.app_data.show_terminal is False:
            return None
        if file_manager.running_from_exe():
            return None

        try:
            input("Ctrl + c or Enter to exit")
        except KeyboardInterrupt:
            pass
