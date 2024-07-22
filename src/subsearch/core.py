import ctypes
import time
from pathlib import Path
from typing import Callable

from subsearch.globals import decorators, log, thread_handle
from subsearch.globals.constants import APP_PATHS, DEVICE_INFO, FILE_PATHS, VIDEO_FILE
from subsearch.globals.dataclasses import Subtitle
from subsearch.gui import screen_manager, system_tray
from subsearch.gui.screens import download_manager
from subsearch.providers import opensubtitles, subsource, yifysubtitles
from subsearch.utils import imdb_lookup, io_file_system, io_toml, string_parser


class Initializer:
    def __init__(self, pref_counter: float) -> None:
        self.start = pref_counter
        log.brackets("Initializing")

        self.api_calls_made: dict[str, int] = {}
        self.downloaded_subtitles = 0
        self.ran_download_tab = False
        self.accepted_subtitles: list[Subtitle] = []
        self.rejected_subtitles: list[Subtitle] = []
        self.manually_accepted_subtitles: list[Subtitle] = []
        self.release_data = string_parser.no_release_data()
        self.provider_urls = string_parser.CreateProviderUrls.no_urls()
        self.file_exist = VIDEO_FILE.file_exist

        log.stdout("Verifing files and paths", level="debug")
        self.setup_file_system()
        self.language_data = io_toml.load_toml_data(FILE_PATHS.language_data)
        self.app_config = io_toml.get_app_config(FILE_PATHS.config)

        log.dataclass(DEVICE_INFO, level="debug", print_allowed=False)
        log.dataclass(self.app_config, level="debug", print_allowed=False)

        log.stdout("Initializing system tray icon", level="debug")
        decorators.enable_system_tray = self.app_config.system_tray
        self.system_tray = system_tray.SystemTray()
        self.system_tray.start()

        if self.file_exist:
            VIDEO_FILE.file_hash = io_file_system.get_file_hash(VIDEO_FILE.file_path)
            log.dataclass(VIDEO_FILE, level="debug", print_allowed=False)
            io_file_system.create_directory(VIDEO_FILE.file_directory)
            self.release_data = string_parser.get_release_data(VIDEO_FILE.filename)
            self.update_imdb_id()
            log.dataclass(self.release_data, level="debug", print_allowed=False)
            provider_urls = string_parser.CreateProviderUrls(self.app_config, self.release_data, self.language_data)
            self.provider_urls = provider_urls.retrieve_urls()
            log.dataclass(self.provider_urls, level="debug", print_allowed=False)
            self.search_kwargs = dict(
                release_data=self.release_data,
                app_config=self.app_config,
                provider_urls=self.provider_urls,
                language_data=self.language_data,
            )

        self.call_conditions = CallConditions(self)
        log.task_completed()

    def update_imdb_id(self) -> None:
        timeout = self.app_config.request_connect_timeout, self.app_config.request_read_timeout
        find_id = imdb_lookup.FindImdbID(
            self.release_data.title,
            self.release_data.year,
            self.release_data.tvseries,
            request_timeout=timeout,
        )
        self.release_data.imdb_id = find_id.imdb_id

    def setup_file_system(self) -> None:

        io_file_system.create_directory(APP_PATHS.tmp_dir)
        io_file_system.create_directory(APP_PATHS.appdata_subsearch)
        io_toml.resolve_on_integrity_failure()
        io_file_system.del_directory_content(APP_PATHS.tmp_dir)
        if self.file_exist:
            io_file_system.create_directory(VIDEO_FILE.subs_dir)
            io_file_system.create_directory(VIDEO_FILE.tmp_dir)

    def all_providers_disabled(self) -> bool:
        if (
            self.app_config.providers["opensubtitles_site"] is False
            and self.app_config.providers["opensubtitles_hash"] is False
            and self.app_config.providers["yifysubtitles_site"] is False
            and self.app_config.providers["subsource_site"] is False
        ):
            return True
        return False


class SubsearchCore(Initializer):
    def __init__(self, pref_counter: float) -> None:
        Initializer.__init__(self, pref_counter)
        ctypes.windll.kernel32.SetConsoleTitleW(f"subsearch - {DEVICE_INFO.subsearch}")
        if not self.file_exist:
            log.brackets("GUI")
            screen_manager.open_screen("search_options")
            log.stdout("Exiting GUI", level="debug")
            return None

        if " " in VIDEO_FILE.filename:
            log.stdout(f"{VIDEO_FILE.filename} contains spaces, result may vary", level="warning")

        if not self.all_providers_disabled():
            log.brackets("Search started")

    @decorators.call_func
    def init_search(self, *providers: Callable[..., None]) -> None:
        thread_handle._create_threads(*providers)
        log.task_completed()

    @decorators.call_func
    def opensubtitles(self) -> None:
        thread_handle._start_search(self, provider=opensubtitles.OpenSubtitles, flag="hash")
        thread_handle._start_search(self, provider=opensubtitles.OpenSubtitles, flag="site")

    @decorators.call_func
    def yifysubtitles(self) -> None:
        thread_handle._start_search(self, provider=yifysubtitles.YifiSubtitles, flag="site")

    @decorators.call_func
    def subsource(self) -> None:
        thread_handle._start_search(self, provider=subsource.Subsource, flag="site")

    @decorators.call_func
    def download_files(self) -> None:
        log.brackets(f"Downloading subtitles")
        index_size = len(self.accepted_subtitles)
        self.accepted_subtitles = sorted(self.accepted_subtitles, key=lambda i: i.precentage_result, reverse=True)
        for index_position, subtitle in enumerate(self.accepted_subtitles):
            if subtitle.provider_name not in self.api_calls_made:
                self.api_calls_made[subtitle.provider_name] = 0
            if not self.api_calls_made[subtitle.provider_name] == self.app_config.api_call_limit:
                if subtitle.provider_name == "subsource":
                    self._handle_subsource_subtitle(index_position, subtitle)
                sub_count = sum(self.api_calls_made.values(), 1)
                io_file_system.download_subtitle(subtitle, sub_count, index_size)
                self.downloaded_subtitles == sub_count
                self.api_calls_made[subtitle.provider_name] += 1
            else:
                s = self.accepted_subtitles.pop(index_position)
                self.rejected_subtitles.append(s)
        log.task_completed()

    def _handle_subsource_subtitle(self, index_position: int, subtitle: Subtitle) -> None:
        if self.app_config.providers["subsource_site"]:
            subsource_api = subsource.GetDownloadUrl()
            download_url = subsource_api.get_url(subtitle)
            if not download_url:
                self.accepted_subtitles.pop(index_position)
                log.stdout(f"{subtitle.provider_name} could not be reached. Removed {subtitle.subtitle_name}")
            else:
                self.accepted_subtitles[index_position].download_url = download_url
                self.accepted_subtitles[index_position].request_data = {}

    @decorators.call_func
    def download_manager(self) -> None:
        log.brackets(f"Download Manager")
        subtitles = self.rejected_subtitles + self.accepted_subtitles
        screen_manager.open_screen("download_manager", subtitles=subtitles)
        self.manually_accepted_subtitles = download_manager.DownloadManager.downloaded_subtitle
        log.task_completed()

    @decorators.call_func
    def extract_files(self) -> None:
        log.brackets("Extracting downloads")
        io_file_system.extract_files_in_dir(VIDEO_FILE.tmp_dir, VIDEO_FILE.subs_dir)
        log.task_completed()

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
        log.brackets("Renaming best match")
        new_name = io_file_system.autoload_rename(VIDEO_FILE.filename, ".srt")
        self.autoload_src = new_name
        log.task_completed()

    @decorators.call_func
    def subtitle_move_best(self, target: Path) -> None:
        log.brackets("Move best match")
        io_file_system.move_and_replace(self.autoload_src, target)
        log.task_completed()

    @decorators.call_func
    def subtitle_move_all(self, target: Path) -> None:
        log.brackets("Move all")
        io_file_system.move_all(VIDEO_FILE.subs_dir, target)
        log.task_completed()

    @decorators.call_func
    def summary_notification(self, elapsed) -> None:
        log.brackets("Summary toast")
        elapsed_summary = f"Finished in {elapsed} seconds"
        tot_num_of_subtitles = len(self.accepted_subtitles) + len(self.rejected_subtitles)
        all_downloaded = self.downloaded_subtitles + len(self.manually_accepted_subtitles)
        matches_downloaded = f"Downloaded: {all_downloaded}/{tot_num_of_subtitles}"
        if all_downloaded > 0:
            msg = "Search Succeeded", f"{matches_downloaded}\n{elapsed_summary}"
            log.stdout(matches_downloaded, hex_color="#a6e3a1")
            self.system_tray.display_toast(*msg)
        elif all_downloaded == 0:
            msg = "Search Failed", f"{matches_downloaded}\n{elapsed_summary}"
            log.stdout(matches_downloaded, hex_color="#f38ba8")
            self.system_tray.display_toast(*msg)

    @decorators.call_func
    def clean_up(self) -> None:
        log.brackets("Cleaning up")
        io_file_system.del_file_type(VIDEO_FILE.subs_dir, ".nfo")
        io_file_system.del_directory_content(APP_PATHS.tmp_dir)
        io_file_system.del_directory(VIDEO_FILE.tmp_dir)
        if io_file_system.directory_is_empty(VIDEO_FILE.subs_dir):
            io_file_system.del_directory(VIDEO_FILE.subs_dir)
        log.task_completed()

    def core_on_exit(self) -> None:
        log.brackets("Exit")
        elapsed = time.perf_counter() - self.start
        self.summary_notification(elapsed)
        self.system_tray.stop()
        log.stdout(f"Finished in {elapsed} seconds", hex_color="#f2cdcd")
        if not self.app_config.show_terminal:
            return None
        if DEVICE_INFO.mode == "executable":
            return None

        try:
            input("Enter to exit")
        except KeyboardInterrupt:
            pass


class CallConditions:

    def __init__(self, cls: Initializer) -> None:
        self.app_config = cls.app_config
        self.file_exist = cls.file_exist
        self.release_data = cls.release_data
        self.provider_urls = cls.provider_urls
        self.language_data = cls.language_data
        self.accepted_subtitles = cls.accepted_subtitles
        self.rejected_subtitles = cls.rejected_subtitles
        self.downloaded_subtitles = cls.downloaded_subtitles

    def check_language_compatibility(self, provider: str) -> bool:
        language = self.app_config.current_language
        if provider in self.language_data[language]:
            return False
        return True

    def all_conditions_true(self, conditions: list[bool]) -> bool:
        if False in conditions:
            return False
        return True

    def call_func(self, *args, **kwargs) -> bool:
        func_name = kwargs["func_name"]
        conditions: dict[str, list[bool]] = {
            "init_search": [self.file_exist],
            "opensubtitles": [
                self.file_exist,
                lambda: self.check_language_compatibility("opensubtitles"),
                self.app_config.providers["opensubtitles_hash"] or self.app_config.providers["opensubtitles_site"],
            ],
            "yifysubtitles": [
                self.file_exist,
                not self.app_config.only_foreign_parts,
                lambda: self.check_language_compatibility("yifysubtitles"),
                not self.release_data.tvseries,
                not self.provider_urls.yifysubtitles == "",
                self.app_config.providers["yifysubtitles_site"],
            ],
            "subsource": [
                self.file_exist,
                not self.app_config.only_foreign_parts,
                lambda: self.check_language_compatibility("subsource"),
                self.app_config.providers["subsource_site"],
            ],
            "download_files": [
                len(self.accepted_subtitles) >= 1
                and self.app_config.automatic_downloads
                or (
                    len(self.accepted_subtitles) >= 1
                    and not self.app_config.automatic_downloads
                    and not self.app_config.always_open
                    and not self.app_config.open_on_no_matches
                ),
            ],
            "download_manager": [
                (
                    (
                        len(self.accepted_subtitles) == 0
                        and len(self.rejected_subtitles) >= 1
                        and self.app_config.open_on_no_matches
                    )
                    or (
                        (len(self.accepted_subtitles) >= 1 or len(self.rejected_subtitles) >= 1)
                        and self.app_config.always_open
                    )
                ),
            ],
            "extract_files": [
                len(self.accepted_subtitles) >= 1,
            ],
            "subtitle_post_processing": [
                self.file_exist,
            ],
            "subtitle_rename": [
                self.app_config.subtitle_post_processing["rename"],
                self.downloaded_subtitles >= 1,
            ],
            "subtitle_move_best": [
                self.app_config.subtitle_post_processing["move_best"],
                self.downloaded_subtitles >= 1,
                not self.app_config.subtitle_post_processing["move_all"],
            ],
            "subtitle_move_all": [
                self.app_config.subtitle_post_processing["move_all"],
                self.downloaded_subtitles > 1,
            ],
            "summary_notification": [
                self.file_exist,
                self.app_config.summary_notification,
            ],
            "clean_up": [self.file_exist],
        }

        return self.all_conditions_true(conditions[func_name])
