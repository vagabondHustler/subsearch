import ctypes
import time
from pathlib import Path

from subsearch.data.constants import APP_PATHS, DEVICE_INFO, FILE_PATHS, VIDEO_FILE
from subsearch.data.data_classes import Subtitle
from subsearch.gui import screen_manager, system_tray
from subsearch.gui.screens import download_manager
from subsearch.providers import opensubtitles, subscene, yifysubtitles
from subsearch.utils import (
    decorators,
    io_file_system,
    io_log,
    io_toml,
    state_manager,
    string_parser,
)


class Initializer:
    def __init__(self, pref_counter: float) -> None:
        self.file_exist = True if VIDEO_FILE else False
        self.setup_file_system()
        state_manager.CoreStateManager()
        self.core_state = state_manager.CoreStateManager()
        self.start = pref_counter
        self.core_state.set_state(self.core_state.state.INITIALIZE)

        self.app_config = io_toml.get_app_config(FILE_PATHS.config)
        io_log.stdout_dataclass(DEVICE_INFO, level="debug", print_allowed=False)
        io_log.stdout_dataclass(self.app_config, level="debug", print_allowed=False)
        decorators.enable_system_tray = self.app_config.system_tray
        self.system_tray = system_tray.SystemTray()
        self.system_tray.start()

        if self.file_exist:
            io_log.stdout_dataclass(VIDEO_FILE, level="debug", print_allowed=False)
            io_file_system.create_directory(VIDEO_FILE.file_directory)

        self.subtitles_found = 0
        self.ran_download_tab = False
        self.accepted_subtitles: list[Subtitle] = []
        self.rejected_subtitles: list[Subtitle] = []
        self.manually_accepted_subtitles: list[Subtitle] = []
        self.language_data = io_toml.load_toml_data(FILE_PATHS.language_data)

        if self.file_exist:
            self.release_data = string_parser.get_release_data(VIDEO_FILE.filename)
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
        io_file_system.create_directory(APP_PATHS.tmp_dir)
        io_file_system.create_directory(APP_PATHS.appdata_subsearch)
        io_toml.resolve_on_integrity_failure()
        if self.file_exist:
            io_file_system.create_directory(VIDEO_FILE.subs_dir)
            io_file_system.create_directory(VIDEO_FILE.tmp_dir)

    def all_providers_disabled(self) -> bool:
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
            screen_manager.open_screen("search_options")
            self.core_state.set_state(self.core_state.state.EXIT)
            return None

        if " " in VIDEO_FILE.filename:
            io_log.stdout(f"{VIDEO_FILE.filename} contains spaces, result may vary", level="warning")

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

    @decorators.call_conditions
    def opensubtitles(self) -> None:
        state_obj = {
            "call_state": self.core_state.state.CALL_OPENSUBTITLES,
            "state_manager": state_manager.OpenSubtitlesStateManager,
        }
        self._search_subtitles(state_obj=state_obj, provider=opensubtitles.OpenSubtitles, flag="hash")
        self._search_subtitles(state_obj=state_obj, provider=opensubtitles.OpenSubtitles, flag="site")

    @decorators.call_conditions
    def subscene(self) -> None:
        state_obj = {
            "call_state": self.core_state.state.CALL_SUBSCENE,
            "state_manager": state_manager.SubsceneStateManager,
        }
        self._search_subtitles(state_obj=state_obj, provider=subscene.Subscene)

    @decorators.call_conditions
    def yifysubtitles(self) -> None:
        state_obj = {
            "call_state": self.core_state.state.CALL_YIFYSUBTITLES,
            "state_manager": state_manager.YifySubtitlesStateManager,
        }
        self._search_subtitles(state_obj=state_obj, provider=yifysubtitles.YifiSubtitles)

    @decorators.call_conditions
    def download_files(self) -> None:
        io_log.stdout_in_brackets(f"Downloading subtitles")
        self.core_state.set_state(self.core_state.state.DOWNLOAD_FILES)
        index_size = len(self.accepted_subtitles)
        for enum, subtitle in enumerate(self.accepted_subtitles, 1):
            io_file_system.download_subtitle(subtitle, enum, index_size)
        self.subtitles_found = index_size
        io_log.stdout("Done with task", level="info", end_new_line=True)

    @decorators.call_conditions
    def manual_download(self) -> None:
        io_log.stdout_in_brackets(f"Manual download")
        self.core_state.set_state(self.core_state.state.MANUAL_DOWNLOAD)
        screen_manager.open_screen("download_manager", subtitles=self.rejected_subtitles)
        self.manually_accepted_subtitles.extend(download_manager.DownloadManager.downloaded_subtitle)
        self.subtitles_found += len(self.manually_accepted_subtitles)
        io_log.stdout("Done with task", level="info", end_new_line=True)

    @decorators.call_conditions
    def extract_files(self) -> None:
        io_log.stdout_in_brackets("Extracting downloads")
        self.core_state.set_state(self.core_state.state.EXTRACT_FILES)
        io_file_system.extract_files_in_dir(VIDEO_FILE.tmp_dir, VIDEO_FILE.subs_dir)
        io_log.stdout("Done with task", level="info", end_new_line=True)

    @decorators.call_conditions
    def subtitle_post_processing(self):
        target = self.app_config.subtitle_post_processing["target_path"]
        resolution = self.app_config.subtitle_post_processing["path_resolution"]
        target_path = io_file_system.create_path_from_string(target, resolution)
        self.subtitle_rename()
        self.subtitle_move_best(target_path)
        self.subtitle_move_all(target_path)

    @decorators.call_conditions
    def subtitle_rename(self) -> None:
        io_log.stdout_in_brackets("Renaming best match")
        self.core_state.set_state(self.core_state.state.AUTOLOAD_RENAME)
        new_name = io_file_system.autoload_rename(VIDEO_FILE.filename, ".srt")
        self.autoload_src = new_name
        io_log.stdout("Done with task", level="info", end_new_line=True)

    @decorators.call_conditions
    def subtitle_move_best(self, target: Path) -> None:
        io_log.stdout_in_brackets("Move best match")
        self.core_state.set_state(self.core_state.state.AUTOLOAD_MOVE)

        io_file_system.move_and_replace(self.autoload_src, target)
        io_log.stdout("Done with task", level="info", end_new_line=True)

    @decorators.call_conditions
    def subtitle_move_all(self, target: Path) -> None:
        io_log.stdout_in_brackets("Move all")
        self.core_state.set_state(self.core_state.state.AUTOLOAD_MOVE_ALL)
        io_file_system.move_all(VIDEO_FILE.subs_dir, target)
        io_log.stdout("Done with task", level="info", end_new_line=True)

    @decorators.call_conditions
    def summary_notification(self, elapsed) -> None:
        io_log.stdout_in_brackets("Summary toast")
        self.core_state.set_state(self.core_state.state.SUMMARY_TOAST)
        elapsed_summary = f"Finished in {elapsed} seconds"
        tot_num_of_subtitles = len(self.accepted_subtitles) + len(self.rejected_subtitles)
        download_summary = f"Matches found {self.subtitles_found}/{tot_num_of_subtitles}"
        if self.subtitles_found > 0:
            msg = "Search Succeeded", f"{download_summary}\n{elapsed_summary}"
            self.system_tray.display_toast(*msg)
        elif self.subtitles_found == 0:
            msg = "Search Failed", f"{download_summary}\n{elapsed_summary}"
            self.system_tray.display_toast(*msg)

    @decorators.call_conditions
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
        self.summary_notification(elapsed)
        io_log.stdout(f"Finished in {elapsed} seconds")
        self.system_tray.stop()
        if not self.app_config.show_terminal:
            return None
        if DEVICE_INFO.mode == "executable":
            return None

        try:
            input("Enter to exit")
        except KeyboardInterrupt:
            pass
