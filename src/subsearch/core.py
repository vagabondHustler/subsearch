import ctypes
import time
from typing import Union

from subsearch.data import __version__, app_paths, device_info, file_data
from subsearch.data.data_objects import DownloadData, PrettifiedDownloadData
from subsearch.gui import screen_manager, system_tray
from subsearch.providers import opensubtitles, subscene, yifysubtitles
from subsearch.utils import (
    app_integrity,
    file_manager,
    io_json,
    log,
    state_machine,
    string_parser,
)


def ignore_condition(func):
    """
    Decorator to check if the conditions for a function are met before executing it.

    Args:
        func (callable): The function to be decorated.

    Returns:
        callable: The wrapped function.

    Example:
        @condition_check
        def my_function(arg1, arg2):
            # Function implementation

        # Call the decorated function
        my_function("value1", "value2")
    """

    def wrapper(*args, **kwargs):
        function = f"{func.__name__}"
        if IgnoreCondition.ignore(function=function, *args, **kwargs):
            module_fn = f"{func.__module__}.{func.__name__}"
            log.stdout(f"Ignoring execution of '{module_fn}' due to satisfied condition(s)", print_allowed=False)
            return None
        return func(*args, **kwargs)

    return wrapper


class Initializer:
    def __init__(self) -> None:
        self.start = time.perf_counter()
        self.core_state = state_machine.CoreStateMachine()
        self.core_state.update_state()
        app_integrity.initialize_application()

        self.app_config = io_json.get_app_config()
        log.stdout_dataclass(device_info, level="debug", print_allowed=False)
        log.stdout_dataclass(self.app_config, level="debug", print_allowed=False)

        system_tray.enable_system_tray = self.app_config.system_tray
        self.system_tray = system_tray.SystemTray()
        self.system_tray.start()

        self.file_exist = True if file_data else False

        if self.file_exist:
            log.stdout_dataclass(file_data, level="debug", print_allowed=False)
            file_manager.create_directory(file_data.subs_directory)
            self.file_hash = file_manager.get_hash(file_data.file_path)
        elif not self.file_exist:
            self.file_hash = ""

        self.subtitles_found = 0
        self.ran_download_tab = False
        self.results: dict[str, list[DownloadData]] = {}
        self.skipped_downloads: dict[str, list[PrettifiedDownloadData]] = {}
        self.skipped_combined: list[PrettifiedDownloadData] = []
        self.downloads: dict[str, int] = {}
        self.language_data = io_json.get_language_data()
        self.foreign_only = io_json.get_json_key("foreign_only")

        for _provider in self.app_config.providers.keys():
            self.results[_provider] = []
            self.skipped_downloads[_provider] = []
            self.downloads[_provider] = 0

        # self.skip_step = SkipStep(self)
        if self.file_exist:
            self.release_data = string_parser.get_release_metadata(file_data.filename, self.file_hash)
            log.stdout_dataclass(self.release_data, level="debug", print_allowed=False)
            create_provider_urls = string_parser.CreateProviderUrls(
                self.file_hash, self.app_config, self.release_data, self.language_data
            )
            self.provider_urls = create_provider_urls.retrieve_urls()
            log.stdout_dataclass(self.provider_urls, level="debug", print_allowed=False)
            self.search_kwargs = dict(
                release_data=self.release_data,
                app_config=self.app_config,
                provider_urls=self.provider_urls,
                language_data=self.language_data,
            )

        self.core_state.update_state()
        if not self.file_exist:
            self.core_state.lock_to_state("no_file")

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

    def download_results(self, results: list[DownloadData]) -> int:
        for result in results:
            downloads = file_manager.download_subtitle(result)
        return downloads


class SubsearchCore(Initializer):
    def __init__(self) -> None:
        Initializer.__init__(self)
        ctypes.windll.kernel32.SetConsoleTitleW(f"subsearch - {__version__}")
        if not self.file_exist:
            self.core_state.lock_to_state("gui")
            screen_manager.open_screen("search_filters")
            self.core_state.lock_to_state("exit")
            return None

        if " " in file_data.filename:
            log.stdout(f"{file_data.filename} contains spaces, result may vary", level="warning")

        if not self.all_providers_disabled():
            log.stdout_in_brackets("Search started")

    @ignore_condition
    def opensubtitles(self) -> None:
        self.core_state.update_state()
        _opensubs = opensubtitles.OpenSubtitles(**self.search_kwargs)
        if self.app_config.providers["opensubtitles_hash"] and self.file_hash != "":
            self.results["opensubtitles_hash"] = _opensubs.parse_hash_results()
        if self.app_config.providers["opensubtitles_site"]:
            self.results["opensubtitles_site"] = _opensubs.parse_site_results()
        self.skipped_downloads["opensubtitles_site"] = _opensubs.sorted_list()

    @ignore_condition
    def subscene(self) -> None:
        self.core_state.update_state()
        _subscene = subscene.Subscene(**self.search_kwargs)
        self.results["subscene_site"] = _subscene.parse_site_results()
        self.skipped_downloads["subscene_site"] = _subscene.sorted_list()

    @ignore_condition
    def yifysubtitles(self) -> None:
        self.core_state.update_state()
        _yifysubs = yifysubtitles.YifiSubtitles(**self.search_kwargs)
        self.results["yifysubtitles_site"] = _yifysubs.parse_site_results()
        self.skipped_downloads["yifysubtitles_site"] = _yifysubs.sorted_list()

    @ignore_condition
    def download_files(self) -> None:
        self.core_state.update_state()
        log.stdout_in_brackets(f"Downloading subtitles")
        for provider, data in self.results.items():
            if self.app_config.providers[provider] is False:
                continue
            if not data:
                continue
            self.subtitles_found = len(data)
            self.downloads[provider] = self.download_results(data)
        for data_list in self.skipped_downloads.values():
            if not data_list:
                continue
            for data in data_list:
                self.skipped_combined.append(data)
        log.stdout("Done with task", level="info", end_new_line=True)

    @ignore_condition
    def manual_download(self) -> None:
        log.stdout_in_brackets(f"Manual_download")
        screen_manager.open_screen("download_manager", data=self.skipped_combined)
        self.ran_download_tab = True
        log.stdout("Done with task", level="info", end_new_line=True)

    @ignore_condition
    def extract_files(self) -> None:
        self.core_state.update_state()
        log.stdout_in_brackets("Extracting downloads")
        file_manager.extract_files(app_paths.tmpdir, file_data.subs_directory, ".zip")
        log.stdout("Done with task", level="info", end_new_line=True)

    @ignore_condition
    def autoload_rename(self) -> None:
        log.stdout_in_brackets("Renaming best match")
        new_name = file_manager.autoload_rename(f"{self.release_data.release}", ".srt")
        self.autoload_src = new_name
        log.stdout("Done with task", level="info", end_new_line=True)

    @ignore_condition
    def autoload_move(self) -> None:
        log.stdout_in_brackets("Renaming best match")
        file_manager.autoload_move(f"{self.release_data.release}", file_data.directory_path, self.autoload_src, ".srt")
        log.stdout("Done with task", level="info", end_new_line=True)

    @ignore_condition
    def clean_up(self) -> None:
        self.core_state.update_state()
        log.stdout_in_brackets("Cleaning up")
        file_manager.clean_up_files(file_data.subs_directory, "nfo")
        file_manager.delete_temp_files(app_paths.tmpdir)
        if file_manager.directory_is_empty(file_data.subs_directory):
            file_manager.del_directory(file_data.subs_directory)
        log.stdout("Done with task", level="info", end_new_line=True)

    @ignore_condition
    def summary_toast(self, elapsed) -> None:
        self.core_state.update_state()
        elapsed_summary = f"Finished in {elapsed} seconds"
        skipped_subtitles = len(self.skipped_combined)
        download_summary = f"Matches found {self.subtitles_found}/{skipped_subtitles}"
        self.core_state.update_state()
        if self.subtitles_found > 0:
            self.system_tray.toast_message(f"Search Succeeded", f"{download_summary}\n{elapsed_summary}")
        elif self.subtitles_found == 0:
            self.system_tray.toast_message(f"Search Failed", f"{download_summary}\n{elapsed_summary}")

    def core_on_exit(self) -> None:
        elapsed = time.perf_counter() - self.start
        self.summary_toast(elapsed)
        log.stdout(f"Finished in {elapsed} seconds")
        self.system_tray.stop()
        if self.app_config.show_terminal is False:
            return None
        if file_manager.running_from_exe():
            return None

        try:
            input("Ctrl + c or Enter to exit")
        except KeyboardInterrupt:
            pass


class IgnoreCondition:
    @staticmethod
    def any_condition_met(conditions: list[bool]) -> bool:
        if any(conditions):
            return True
        return False

    @staticmethod
    def ignore(cls: Union["SubsearchCore", "Initializer"], *args, **kwargs) -> bool:
        """
        Check if the conditions for a given function are met and cls should be ignored.

        Args:
            cls (Union["AppSteps", "Initializer"]): An instance of the class "AppSteps" or "Initializer".
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            bool: True if any condition is met, False otherwise.

        Raises:
            KeyError: If the "function" keyword argument is not provided.

        Example:
            is_condition_met = core_func_conditions(instance, function="core_opensubtitles")
        """
        if not cls.file_exist:
            return True
        function = kwargs["function"]
        conditions = {
            "opensubtitles": [
                cls.foreign_only,
                not io_json.check_language_compatibility("opensubtitles"),
                not (cls.app_config.providers["opensubtitles_hash"] and cls.app_config.providers["opensubtitles_site"]),
            ],
            "subscene": [
                not io_json.check_language_compatibility("subscene"),
                not cls.app_config.providers["subscene_site"],
            ],
            "yifysubtitles": [
                cls.foreign_only,
                not io_json.check_language_compatibility("yifysubtitles"),
                cls.release_data.tvseries,
                cls.provider_urls.yifysubtitles == "",
                not cls.app_config.providers["yifysubtitles_site"],
            ],
            "download_files": [not any(cls.results.values())],
            "manual_download": [
                not cls.skipped_combined,
                cls.app_config.manual_download_fail and sum(v for v in cls.downloads.values()) > 0,
                cls.app_config.manual_download_mode and sum(v for v in cls.downloads.values()) < 1,
            ],
            "extract_files": [cls.ran_download_tab, cls.all_providers_disabled()],
            "autoload_rename": [not cls.app_config.autoload_rename],
            "autoload_move": [not cls.app_config.autoload_move],
            "summary_toast": [not cls.app_config.toast_summary],
            "clean_up": [],  # No conditions defined for this function
        }
        return IgnoreCondition.any_condition_met(conditions[function])
