import ctypes
import time
from typing import Union

from subsearch.data.constants import APP_PATHS, DEVICE_INFO, VIDEO_FILE
from subsearch.data.data_classes import Subtitle
from subsearch.gui import screen_manager, system_tray
from subsearch.providers import opensubtitles, subscene, yifysubtitles
from subsearch.utils import (
    app_health,
    io_file_system,
    io_json,
    io_log,
    state_manager,
    string_parser,
)


def call_conditions(func):
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
        if not CallCondition.conditions(function=function, *args, **kwargs):
            module_fn = f"{func.__module__}.{func.__name__}"
            io_log.stdout(f"Call conditions for '{module_fn}', not met", print_allowed=False)
            return None
        return func(*args, **kwargs)

    return wrapper


class Initializer:
    def __init__(self, pref_counter: float) -> None:
        self.start = pref_counter
        self.core_state = state_manager.CoreStateManager()
        self.core_state.set_state(self.core_state.state.INITIALIZE)
        self.file_exist = True if VIDEO_FILE else False
        self.setup_file_system()

        self.app_config = io_json.get_app_config()
        io_log.stdout_dataclass(DEVICE_INFO, level="debug", print_allowed=False)
        io_log.stdout_dataclass(self.app_config, level="debug", print_allowed=False)

        system_tray.enable_system_tray = self.app_config.system_tray
        self.system_tray = system_tray.SystemTray()
        self.system_tray.start()

        if self.file_exist:
            io_log.stdout_dataclass(VIDEO_FILE, level="debug", print_allowed=False)
            io_file_system.create_directory(VIDEO_FILE.file_directory)

        self.subtitles_found = 0
        self.ran_download_tab = False
        self.accepted_subtitles: list[Subtitle] = []
        self.rejected_subtitles: list[Subtitle] = []
        self.language_data = io_json.get_language_data()
        self.foreign_only = io_json.get_json_key("foreign_only")

        if self.file_exist:
            self.release_data = string_parser.get_release_data(VIDEO_FILE.file_name)
            io_log.stdout_dataclass(self.release_data, level="debug", print_allowed=False)
            provider_urls = string_parser.CreateProviderUrls(self.app_config, self.release_data, self.language_data)
            self.provider_urls = provider_urls.retrieve_urls()
            io_log.stdout_dataclass(self.provider_urls, level="debug", print_allowed=False)
            self.search_kwargs = dict(
                release_data=self.release_data,
                app_config=self.app_config,
                provider_urls=self.provider_urls,
                language_data=self.language_data,
            )

        self.core_state.set_state(self.core_state.state.INITIALIZED)
        if not self.file_exist:
            self.core_state.set_state(self.core_state.state.NO_FILE)

    def setup_file_system(self) -> None:
        """
        Initializes the application by performing necessary checks and setup.

        Returns:
            None.
        """
        app_health.resolve_on_integrity_failure()
        io_file_system.create_directory(APP_PATHS.tmp_dir)
        io_file_system.create_directory(APP_PATHS.app_data_local)
        if self.file_exist:
            io_file_system.create_directory(VIDEO_FILE.subs_dir)
            io_file_system.create_directory(VIDEO_FILE.tmp_dir)
        io_json.create_config_file()

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


class SubsearchCore(Initializer):
    def __init__(self, pref_counter: float) -> None:
        Initializer.__init__(self, pref_counter)
        ctypes.windll.kernel32.SetConsoleTitleW(f"subsearch - {DEVICE_INFO.subsearch}")
        if not self.file_exist:
            self.core_state.set_state(self.core_state.state.GUI)
            screen_manager.open_screen("search_filters")
            self.core_state.set_state(self.core_state.state.EXIT)
            return None

        if " " in VIDEO_FILE.file_name:
            io_log.stdout(f"{VIDEO_FILE.file_name} contains spaces, result may vary", level="warning")

        if not self.all_providers_disabled():
            io_log.stdout_in_brackets("Search started")

    def _search_subtitles(self, **kwargs) -> None:
        flag = kwargs.get("flag")
        self.core_state.set_state(kwargs["state_obj"]["call_state"])
        provider_state = kwargs["state_obj"]["state_manager"]()
        provider_state.set_state(provider_state.state.WORKING)
        search_provider = kwargs["provider"](**self.search_kwargs)
        if flag:
            search_provider.start_search(flag=flag)
        else:
            search_provider.start_search()
        self.accepted_subtitles.extend(search_provider.accepted_subtitles)
        self.rejected_subtitles.extend(search_provider.rejected_subtitles)
        provider_state.set_state(provider_state.state.FINNISHED)

    @call_conditions
    def opensubtitles(self) -> None:
        state_obj = {
            "call_state": self.core_state.state.CALL_OPENSUBTITLES,
            "state_manager": state_manager.OpenSubtitlesStateManager,
        }
        self._search_subtitles(state_obj=state_obj, provider=opensubtitles.OpenSubtitles, flag="hash")
        self._search_subtitles(state_obj=state_obj, provider=opensubtitles.OpenSubtitles, flag="site")

    @call_conditions
    def subscene(self) -> None:
        state_obj = {
            "call_state": self.core_state.state.CALL_SUBSCENE,
            "state_manager": state_manager.SubsceneStateManager,
        }
        self._search_subtitles(state_obj=state_obj, provider=subscene.Subscene)

    @call_conditions
    def yifysubtitles(self) -> None:
        state_obj = {
            "call_state": self.core_state.state.CALL_YIFYSUBTITLES,
            "state_manager": state_manager.YifySubtitlesStateManager,
        }
        self._search_subtitles(state_obj=state_obj, provider=yifysubtitles.YifiSubtitles)

    @call_conditions
    def download_files(self) -> None:
        io_log.stdout_in_brackets(f"Downloading subtitles")
        self.core_state.set_state(self.core_state.state.DOWNLOAD_FILES)
        index_size = len(self.accepted_subtitles)
        for enum, subtitle in enumerate(self.accepted_subtitles, 1):
            io_file_system.download_subtitle(subtitle, enum, index_size)
        self.subtitles_found = index_size
        io_log.stdout("Done with task", level="info", end_new_line=True)

    @call_conditions
    def manual_download(self) -> None:
        io_log.stdout_in_brackets(f"Manual download")
        self.core_state.set_state(self.core_state.state.MANUAL_DOWNLOAD)
        for data_list in self.rejected_subtitles.values():
            if not data_list:
                continue
            for data in data_list:
                self.skipped_combined.append(data)
        screen_manager.open_screen("download_manager", data=self.skipped_combined)
        self.ran_download_tab = True
        io_log.stdout("Done with task", level="info", end_new_line=True)

    @call_conditions
    def extract_files(self) -> None:
        io_log.stdout_in_brackets("Extracting downloads")
        self.core_state.set_state(self.core_state.state.EXTRACT_FILES)
        io_file_system.extract_files_in_dir(VIDEO_FILE.tmp_dir, VIDEO_FILE.subs_dir)
        io_log.stdout("Done with task", level="info", end_new_line=True)

    @call_conditions
    def autoload_rename(self) -> None:
        io_log.stdout_in_brackets("Renaming best match")
        self.core_state.set_state(self.core_state.state.AUTOLOAD_RENAME)
        new_name = io_file_system.autoload_rename(VIDEO_FILE.file_name, ".srt")
        self.autoload_src = new_name
        io_log.stdout("Done with task", level="info", end_new_line=True)

    @call_conditions
    def autoload_move(self) -> None:
        io_log.stdout_in_brackets("Move best match")
        self.core_state.set_state(self.core_state.state.AUTOLOAD_MOVE)
        io_file_system.move_and_replace(self.autoload_src, VIDEO_FILE.file_directory)
        io_log.stdout("Done with task", level="info", end_new_line=True)

    @call_conditions
    def summary_toast(self, elapsed) -> None:
        io_log.stdout_in_brackets("Summary toast")
        self.core_state.set_state(self.core_state.state.SUMMARY_TOAST)
        elapsed_summary = f"Finished in {elapsed} seconds"
        skipped_subtitles = 0
        download_summary = f"Matches found {self.subtitles_found}/{skipped_subtitles}"
        if self.subtitles_found > 0:
            msg = "Search Succeeded", f"{download_summary}\n{elapsed_summary}"
            self.system_tray.toast_message(*msg)
        elif self.subtitles_found == 0:
            msg = "Search Failed", f"{download_summary}\n{elapsed_summary}"
            self.system_tray.toast_message(*msg)
            
    @call_conditions
    def clean_up(self) -> None:
        io_log.stdout_in_brackets("Cleaning up")
        self.core_state.set_state(self.core_state.state.CLEAN_UP)
        io_file_system.del_file_type(VIDEO_FILE.subs_dir, ".nfo")
        io_file_system.del_directory_content(APP_PATHS.tmp_dir)
        io_file_system.del_directory(VIDEO_FILE.tmp_dir)
        if io_file_system.directory_is_empty(VIDEO_FILE.file_directory):
            io_file_system.del_directory(VIDEO_FILE.subs_dir)
        io_log.stdout("Done with task", level="info", end_new_line=True)

    def core_on_exit(self) -> None:
        elapsed = time.perf_counter() - self.start
        self.summary_toast(elapsed)
        io_log.stdout(f"Finished in {elapsed} seconds")
        self.system_tray.stop()
        if self.app_config.show_terminal is False:
            return None
        if DEVICE_INFO.mode == "executable":
            return None

        try:
            input("Ctrl + c or Enter to exit")
        except KeyboardInterrupt:
            pass
        self.core_state.set_state(self.core_state.state.EXIT)


class CallCondition:
    @staticmethod
    def all_conditions_met(conditions: list[bool]) -> bool:
        if all(condition for condition in conditions):
            return True
        return False

    @staticmethod
    def conditions(cls: Union["SubsearchCore", "Initializer"], *args, **kwargs) -> bool:
        if not cls.file_exist:
            return False
        function = kwargs["function"]
        conditions = {
            "opensubtitles": [
                not cls.foreign_only,
                io_json.check_language_compatibility("opensubtitles"),
                cls.app_config.providers["opensubtitles_hash"] or cls.app_config.providers["opensubtitles_site"],
            ],
            "subscene": [
                io_json.check_language_compatibility("subscene"),
                cls.app_config.providers["subscene_site"],
            ],
            "yifysubtitles": [
                not cls.foreign_only,
                io_json.check_language_compatibility("yifysubtitles"),
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
            "extract_files": [
                len(cls.accepted_subtitles) >= 1
                or (
                    len(cls.accepted_subtitles) == 0
                    and len(cls.rejected_subtitles) >= 1
                    and cls.app_config.manual_download_on_fail
                ),
            ],
            "autoload_rename": [cls.app_config.autoload_rename, cls.subtitles_found > 1],
            "autoload_move": [cls.app_config.autoload_move, cls.subtitles_found > 1],
            "summary_toast": [cls.app_config.toast_summary],
        }
        return CallCondition.all_conditions_met(conditions[function])
