import ctypes
import time

from subsearch.data import __version__, video_data
from subsearch.data.data_objects import DownloadMetaData, FormattedMetadata
from subsearch.gui import tab_manager
from subsearch.providers import opensubtitles, subscene, yifysubtitles
from subsearch.utils import file_manager, io_json, io_winreg, log, string_parser


class Initializer:
    def __init__(self) -> None:
        self.app_config = io_json.get_app_config()
        if video_data is not None:
            self.file_exist = True
            self.file_hash = file_manager.get_hash(video_data.file_path)
        else:
            self.file_exist = False
            self.file_hash = ""
        self.results: dict[str, list[DownloadMetaData]] = {}
        self.skipped_downloads: dict[str, list[FormattedMetadata]] = {}
        self.skipped_combined: list[FormattedMetadata] = []
        self.downloads: dict[str, int] = {}
        self.language_data = io_json.get_language_data()

        for provider in self.app_config.providers.keys():
            self.results[provider] = []
            self.skipped_downloads[provider] = []
            self.downloads[provider] = 0

        self.ran_download_tab = False
        self.skip_step = SkipStep(self)
        if self.file_exist:
            self.release_data = string_parser.get_release_metadata(video_data.filename, self.file_hash)
            create_provider_urls = string_parser.CreateProviderUrls(
                self.file_hash, self.app_config, self.release_data, self.language_data
            )
            self.provider_urls = create_provider_urls.retrieve_urls()
            self.search_kwargs = dict(
                release_data=self.release_data,
                app_config=self.app_config,
                provider_urls=self.provider_urls,
                language_data=self.language_data,
            )
            log.set_logger_data(**self.search_kwargs)
            log.output_parameters()

    def all_providers_disabled(self) -> bool:
        self.app_config = io_json.get_app_config()
        if (
            self.app_config.providers["subscene_site"] is False
            and self.app_config.providers["opensubtitles_site"] is False
            and self.app_config.providers["opensubtitles_hash"] is False
            and self.app_config.providers["yifysubtitles_site"] is False
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
        if io_winreg.registry_key_exists() is False and io_json.get_json_key("context_menu"):
            io_json.set_default_json()
            io_winreg.add_context_menu()
        if io_winreg.registry_key_exists() and io_winreg.key_no_value() and io_json.get_json_key("context_menu"):
            io_winreg.add_context_menu()
        file_manager.make_necessary_directories()
        if self.file_exist is False:
            tab_manager.open_tab("search")
            return None

        if " " in video_data.filename:
            log.warning_spaces_in_filename()
        log.output_header("Search started")

    def _provider_opensubtitles(self) -> None:
        if self.skip_step.opensubtitles():
            return None
        # log.output_header("Searching on opensubtitles")
        _opensubs = opensubtitles.OpenSubtitles(**self.search_kwargs)
        if self.app_config.providers["opensubtitles_hash"] and self.file_hash != "":
            self.results["opensubtitles_hash"] = _opensubs.parse_hash_results()
        if self.app_config.providers["opensubtitles_site"]:
            self.results["opensubtitles_site"] = _opensubs.parse_site_results()
        self.skipped_downloads["opensubtitles_site"] = _opensubs._sorted_list()

    def _provider_subscene(self) -> None:
        if self.skip_step.subscene():
            return None
        _subscene = subscene.Subscene(**self.search_kwargs)
        self.results["subscene_site"] = _subscene.parse_site_results()
        self.skipped_downloads["subscene_site"] = _subscene._sorted_list()

    def _provider_yifysubtitles(self) -> None:
        if self.skip_step.yifysubtitles():
            return None
        _yifysubs = yifysubtitles.YifiSubtitles(**self.search_kwargs)
        self.results["yifysubtitles_site"] = _yifysubs.parse_site_results()
        self.skipped_downloads["yifysubtitles_site"] = _yifysubs._sorted_list()

    def _download_files(self) -> None:
        if self.skip_step.download_files():
            return None
        log.output_header(f"Downloading subtitles")
        for provider, data in self.results.items():
            if self.app_config.providers[provider] is False:
                continue
            if not data:
                continue
            self.downloads[provider] = self.download_results(data)
        log.output_done_with_tasks(end_new_line=True)

    def _not_downloaded(self) -> None:
        if self.skip_step.not_downloaded():
            return None
        for data_list in self.skipped_downloads.values():
            if not data_list:
                continue
            for data in data_list:
                self.skipped_combined.append(data)

        if self.skipped_combined:
            tab_manager.open_tab("download", formatted_data=self.skipped_combined)
            self.ran_download_tab = True
        log.output_done_with_tasks(end_new_line=True)

    def _extract_zip_files(self) -> None:
        if self.skip_step.extract_zip():
            return None
        log.output_header("Extracting downloads")
        file_manager.extract_files(video_data.tmp_directory, video_data.subs_directory, ".zip")
        log.output_done_with_tasks(end_new_line=True)

    def _clean_up(self) -> None:
        if self.file_exist is False:
            return None
        if self.app_config.rename_best_match:
            log.output_header("Renaming best match")
            file_manager.rename_best_match(f"{self.release_data.release}.srt", video_data.directory_path, ".srt")
            log.output_done_with_tasks(end_new_line=True)

        log.output_header("Cleaning up")
        file_manager.clean_up_files(video_data.subs_directory, "nfo")
        file_manager.del_directory(video_data.tmp_directory)
        if file_manager.directory_is_empty(video_data.subs_directory):
            file_manager.del_directory(video_data.subs_directory)
        log.output_done_with_tasks(end_new_line=True)

    def _pre_exit(self) -> None:
        elapsed = time.perf_counter() - self.start
        log.output(f"Finished in {elapsed} seconds")

        if self.app_config.show_terminal is False:
            return None
        if file_manager.running_from_exe():
            return None

        try:
            input("Ctrl + c or Enter to exit")
        except KeyboardInterrupt:
            pass


class SkipStep:
    def __init__(self, cls):
        self.cls = cls

    def opensubtitles(self) -> bool:
        if self.cls.file_exist is False:
            return True
        if io_json.check_language_compatibility("opensubtitles") is False:
            return True
        if (
            self.cls.app_config.providers["opensubtitles_hash"] is False
            and self.cls.app_config.providers["opensubtitles_site"] is False
        ):
            return True
        return False

    def subscene(self) -> bool:
        if self.cls.file_exist is False:
            return True
        if io_json.check_language_compatibility("subscene") is False:
            return True
        if self.cls.app_config.providers["subscene_site"] is False:
            return True
        return False

    def yifysubtitles(self) -> bool:
        if self.cls.file_exist is False:
            return True
        if io_json.check_language_compatibility("yifysubtitles") is False:
            return True
        if self.cls.release_data.tvseries:
            return True
        if self.cls.provider_urls.yifysubtitles == "N/A":
            return True
        if self.cls.app_config.providers["yifysubtitles_site"] is False:
            return True
        return False

    def download_files(self) -> bool:
        if self.cls.file_exist is False:
            return True
        if not any(self.cls.results.values()):
            return True
        return False

    def not_downloaded(self) -> bool:
        if self.cls.file_exist is False:
            return True
        number_of_downloads = sum(v for v in self.cls.downloads.values())
        if self.cls.app_config.manual_download_fail and number_of_downloads > 0:
            return True

        if self.cls.app_config.manual_download_mode and number_of_downloads < 1:
            return False
        return False

    def extract_zip(self) -> bool:
        if self.cls.file_exist is False:
            return True
        if self.cls.ran_download_tab:
            return True
        if self.cls.all_providers_disabled():
            return True
        return False
