import ctypes
import secrets
import time
from pathlib import Path
from subsearch.globals import propagating_thread
from subsearch.globals.constants import APP_PATHS, DEVICE_INFO, FILE_PATHS, VIDEO_FILE, VERSION
from subsearch.globals.dataclasses import Subtitle
from subsearch.globals import decorators
from subsearch.gui import screen_manager, system_tray
from subsearch.gui.screens import download_manager
from subsearch.providers import opensubtitles, subscene, yifysubtitles
from subsearch.utils import (
    io_file_system,
    io_log,
    io_toml,
    string_parser,
)


class Initializer:
    def __init__(self, pref_counter: float) -> None:
        io_log.log.stdout(f"Loading components...", level="info", end_new_line=True)
        self.file_exist = True if VIDEO_FILE else False
        self.setup_file_system()
        self.start = pref_counter

        self.app_config = io_toml.get_app_config(FILE_PATHS.config)
        io_log.log.dataclass(DEVICE_INFO, level="debug", print_allowed=False)
        io_log.log.dataclass(self.app_config, level="debug", print_allowed=False)
        decorators.enable_system_tray = self.app_config.system_tray
        self.system_tray = system_tray.SystemTray()
        self.system_tray.start()

        if self.file_exist:
            VIDEO_FILE.file_hash = io_file_system.get_file_hash(VIDEO_FILE.file_path)
            io_log.log.dataclass(VIDEO_FILE, level="debug", print_allowed=False)
            io_file_system.create_directory(VIDEO_FILE.file_directory)

        self.downloaded_subtitles = 0
        self.ran_download_tab = False
        self.accepted_subtitles: list[Subtitle] = []
        self.rejected_subtitles: list[Subtitle] = []
        self.manually_accepted_subtitles: list[Subtitle] = []
        self.language_data = io_toml.load_toml_data(FILE_PATHS.language_data)

        if self.file_exist:
            self.release_data = string_parser.get_release_data(VIDEO_FILE.filename)
            io_log.log.dataclass(self.release_data, level="debug", print_allowed=False)
            provider_urls = string_parser.CreateProviderUrls(self.app_config, self.release_data, self.language_data)
            self.provider_urls = provider_urls.retrieve_urls()
            io_log.log.dataclass(self.provider_urls, level="debug", print_allowed=False)
            self.search_kwargs = dict(
                release_data=self.release_data,
                app_config=self.app_config,
                provider_urls=self.provider_urls,
                language_data=self.language_data,
            )

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
            screen_manager.open_screen("search_options")
            return None

        if " " in VIDEO_FILE.filename:
            io_log.log.stdout(f"{VIDEO_FILE.filename} contains spaces, result may vary", level="warning")

        if not self.all_providers_disabled():
            io_log.log.brackets("Search started")

    def search_for_subtitles(self, *tasks) -> None:
        propagating_thread.handle_tasks(*tasks)
        io_log.log.task_completed()

    def start_search(self, provider, flag: str = "") -> None:
        search_provider = provider(**self.search_kwargs)
        if flag:
            search_provider.start_search(flag=flag)
        else:
            search_provider.start_search()
        self.accepted_subtitles.extend(search_provider.accepted_subtitles)
        self.rejected_subtitles.extend(search_provider.rejected_subtitles)

    @decorators.call_func
    def opensubtitles(self) -> None:
        self.start_search(provider=opensubtitles.OpenSubtitles, flag="hash")
        self.start_search(provider=opensubtitles.OpenSubtitles, flag="site")

    @decorators.call_func
    def subscene(self) -> None:
        self.start_search(provider=subscene.Subscene)

    @decorators.call_func
    def yifysubtitles(self) -> None:
        self.start_search(provider=yifysubtitles.YifiSubtitles)

    @decorators.call_func
    def download_files(self) -> None:
        io_log.log.brackets(f"Downloading subtitles")
        index_size = len(self.accepted_subtitles)
        for enum, subtitle in enumerate(self.accepted_subtitles, 1):
            io_file_system.download_subtitle(subtitle, enum, index_size)
            self.downloaded_subtitles += 1
        self.subtitles_found = index_size
        io_log.log.task_completed()

    @decorators.call_func
    def download_manager(self) -> None:
        io_log.log.brackets(f"Download Manager")
        subtitles = self.rejected_subtitles + self.accepted_subtitles
        screen_manager.open_screen("download_manager", subtitles=subtitles)
        self.manually_accepted_subtitles.extend(download_manager.DownloadManager.downloaded_subtitle)
        self.subtitles_found += len(self.manually_accepted_subtitles)
        io_log.log.task_completed()

    @decorators.call_func
    def extract_files(self) -> None:
        io_log.log.brackets("Extracting downloads")
        io_file_system.extract_files_in_dir(VIDEO_FILE.tmp_dir, VIDEO_FILE.subs_dir)
        io_log.log.task_completed()

    @decorators.call_func
    def subtitle_post_processing(self):
        target = self.app_config.subtitle_post_processing["target_path"]
        resolution = self.app_config.subtitle_post_processing["path_resolution"]
        target_path = io_file_system.create_path_from_string(target, resolution)
        self.subtitle_rename()
        self.subtitle_move_best(target_path)
        self.subtitle_move_all(target_path)

    @decorators.call_func
    def subtitle_rename(self) -> None:
        io_log.log.brackets("Renaming best match")
        new_name = io_file_system.autoload_rename(VIDEO_FILE.filename, ".srt")
        self.autoload_src = new_name
        io_log.log.task_completed()

    @decorators.call_func
    def subtitle_move_best(self, target: Path) -> None:
        io_log.log.brackets("Move best match")
        io_file_system.move_and_replace(self.autoload_src, target)
        io_log.log.task_completed()

    @decorators.call_func
    def subtitle_move_all(self, target: Path) -> None:
        io_log.log.brackets("Move all")
        io_file_system.move_all(VIDEO_FILE.subs_dir, target)
        io_log.log.task_completed()

    @decorators.call_func
    def summary_notification(self, elapsed) -> None:
        io_log.log.brackets("Summary toast")
        elapsed_summary = f"Finished in {elapsed} seconds"
        tot_num_of_subtitles = len(self.accepted_subtitles) + len(self.rejected_subtitles)
        matches_downloaded = f"Downloaded: {self.downloaded_subtitles}/{tot_num_of_subtitles}"
        if self.downloaded_subtitles > 0:
            msg = "Search Succeeded", f"{matches_downloaded}\n{elapsed_summary}"
            io_log.log.stdout(matches_downloaded, hex_color="#a6e3a1")
            self.system_tray.display_toast(*msg)
        elif self.downloaded_subtitles == 0:
            msg = "Search Failed", f"{matches_downloaded}\n{elapsed_summary}"
            io_log.log.stdout(matches_downloaded, hex_color="#f38ba8")
            self.system_tray.display_toast(*msg)

    @decorators.call_func
    def clean_up(self) -> None:
        io_log.log.brackets("Cleaning up")
        io_file_system.del_file_type(VIDEO_FILE.subs_dir, ".nfo")
        io_file_system.del_directory_content(APP_PATHS.tmp_dir)
        io_file_system.del_directory(VIDEO_FILE.tmp_dir)
        if io_file_system.directory_is_empty(VIDEO_FILE.subs_dir):
            io_file_system.del_directory(VIDEO_FILE.subs_dir)
        io_log.log.task_completed()

    def core_on_exit(self) -> None:
        elapsed = time.perf_counter() - self.start
        self.summary_notification(elapsed)
        io_log.log.stdout(f"Finished in {elapsed} seconds", hex_color="#f2cdcd")
        self.system_tray.stop()
        if not self.app_config.show_terminal:
            return None
        if DEVICE_INFO.mode == "executable":
            return None

        try:
            input("Enter to exit")
        except KeyboardInterrupt:
            pass
