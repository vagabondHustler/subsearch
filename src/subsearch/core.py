import ctypes
import time
from pathlib import Path
from typing import Any, Callable

from subsearch import threading_utils, ui
from subsearch.ui.system_tray import SystemTray
from subsearch.decorators.orchestration import call_func
from subsearch.logger import log
from subsearch.model import Subtitle
from subsearch.runtime.constants import APP_PATHS, DEVICE_INFO, FILE_PATHS, VIDEO_FILE
from subsearch.providers import opensubtitles, subsource, yifysubtitles
from subsearch.io import (
    imdb_lookup,
    io_file_system,
    io_toml,
    io_winreg,
    string_parser,
)


class Initializer:
    def __init__(self, pref_counter: float) -> None:
        self.start = pref_counter
        log.brackets("Initializing")

        self.api_calls_made: dict[str, int] = {}
        self.ran_download_tab = False
        self.accepted_subtitles: list[Subtitle] = []
        self.rejected_subtitles: list[Subtitle] = []
        self.manually_accepted_subtitles: list[Subtitle] = []
        self.release_data = string_parser.no_release_data()
        self.provider_urls = string_parser.CreateProviderUrls.no_urls()
        self.file_exist = VIDEO_FILE.file_exist
        self.autoload_src: Path = Path("")

        self.downloaded_subtitles: int = 0
        self.downloaded_subtitle_archives: int = 0
        self.extracted_subtitle_archives: int = 0
        self.user_downloaded_files = False

        log.stdout("Verifing files and paths", level="debug")
        self.setup_file_system()
        self.language_data = io_toml.load_toml_data(FILE_PATHS.language_data)
        self.app_config = io_toml.get_app_config(FILE_PATHS.config)
        if not io_winreg.check_long_paths_enabled():
            self._notify_user()

        log.dataclass(DEVICE_INFO, level="debug", print_allowed=False)
        log.dataclass(self.app_config, level="debug", print_allowed=False)

        log.stdout("Initializing system tray icon", level="debug")
        self.system_tray = SystemTray(enabled=self.app_config.system_tray)
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
        find_id = imdb_lookup.FindImdbID(
            self.release_data.title,
            self.release_data.year,
            self.release_data.tvseries,
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
            self.app_config.providers["opensubtitles"] is False
            and self.app_config.providers["yifysubtitles_site"] is False
            and self.app_config.providers["subsource_site"] is False
        ):
            return True
        return False

    def prevent_conflicting_config_settings(self) -> None:
        # TODO
        # make settings exclusive in GUI
        if self.app_config.open_manager_on_no_matches and self.app_config.always_open_manager:
            self.app_config.open_manager_on_no_matches = False
            io_toml.update_toml_key(FILE_PATHS.config, "download.open_manager_on_no_matches", False)
        if (
            self.app_config.post_processing["move_best"]
            and self.app_config.post_processing["move_all"]
        ):
            self.app_config.post_processing["move_best"] = False
            io_toml.update_toml_key(FILE_PATHS.config, "post_processing.move_best", False)

    def _notify_user(self) -> None:
        log.stdout("Win32 long paths disabled; paths >260 chars may fail. Set LongPathsEnabled=1 and reboot.")
        log.stdout("https://github.com/vagabondHustler/Win32LongPaths")


class SubsearchCore(Initializer):
    def __init__(self, pref_counter: float) -> None:
        Initializer.__init__(self, pref_counter)
        ctypes.windll.kernel32.SetConsoleTitleW(f"subsearch - {DEVICE_INFO.subsearch}")
        if not self.file_exist:
            log.brackets("GUI")
            ui.open_settings_window()
            log.stdout("Exiting GUI", level="debug")
            self.prevent_conflicting_config_settings()
            return None

        if " " in VIDEO_FILE.filename:
            log.stdout(f"{VIDEO_FILE.filename} contains spaces, result may vary", level="warning")

        if not self.all_providers_disabled():
            self.prevent_conflicting_config_settings()
            log.brackets("Search started")

    @call_func
    def init_search(self, *providers: Callable[..., None]) -> None:
        threading_utils._create_threads(*providers)
        log.task_completed()

    def _start_search(self, provider: Callable[..., Any], flag: str) -> None:
        search_provider = provider(**self.search_kwargs)
        search_provider.start_search(flag=flag)
        self.accepted_subtitles.extend(search_provider.accepted_subtitles)
        self.rejected_subtitles.extend(search_provider.rejected_subtitles)

    @call_func
    def opensubtitles(self) -> None:
        self._start_search(provider=opensubtitles.OpenSubtitles, flag="site")

    @call_func
    def yifysubtitles(self) -> None:
        self._start_search(provider=yifysubtitles.YifiSubtitles, flag="site")

    @call_func
    def subsource(self) -> None:
        self._start_search(provider=subsource.Subsource, flag="site")

    @call_func
    def download_files(self) -> None:
        log.brackets(f"Downloading subtitles")
        self.accepted_subtitles = sorted(self.accepted_subtitles, key=lambda i: i.precentage_result, reverse=True)
        keep: list[Subtitle] = []
        for subtitle in self.accepted_subtitles:
            if subtitle.provider_name not in self.api_calls_made:
                self.api_calls_made[subtitle.provider_name] = 0
            if self.api_calls_made[subtitle.provider_name] == self.app_config.api_call_limit:
                self.rejected_subtitles.append(subtitle)
                continue
            if subtitle.provider_name == "subsource":
                resolved = self._handle_subsource_subtitle(subtitle)
                if resolved is None:
                    continue
                subtitle = resolved
            sub_count = sum(self.api_calls_made.values(), 1)
            index_size = len(self.accepted_subtitles)
            io_file_system.download_subtitle(subtitle, sub_count, index_size)
            self.downloaded_subtitles += 1
            self.api_calls_made[subtitle.provider_name] += 1
            keep.append(subtitle)
        self.accepted_subtitles = keep
        log.task_completed()

    def _handle_subsource_subtitle(self, subtitle: Subtitle) -> Subtitle | None:
        if not self.app_config.providers["subsource_site"]:
            return subtitle
        subsource_api = subsource.GetDownloadUrl()
        download_url = subsource_api.get_url(subtitle)
        if not download_url:
            log.stdout(f"{subtitle.provider_name} could not be reached. Removed {subtitle.subtitle_name}")
            return None
        subtitle.download_url = download_url
        subtitle.request_data = {}
        return subtitle

    @call_func
    def download_manager(self) -> None:
        log.brackets(f"Download Manager")
        subtitles = self.rejected_subtitles + self.accepted_subtitles
        self.manually_accepted_subtitles = ui.open_settings_window(subtitles)
        self.downloaded_subtitles += len(self.manually_accepted_subtitles)
        log.task_completed()

    @call_func
    def subtitle_post_processing(self) -> None:
        target = self.app_config.post_processing["target_path"]
        resolution = self.app_config.post_processing["path_resolution"]
        create_missing_folder = self.app_config.post_processing["create_missing_folder"]
        target_path = io_file_system.create_path_from_string(target, resolution, create_missing_folder)
        self.downloaded_subtitle_archives = io_file_system.count_files_in_directory(VIDEO_FILE.tmp_dir)
        self.extract_files()
        self.extracted_subtitle_archives = io_file_system.count_files_in_directory(VIDEO_FILE.subs_dir, [".srt"])
        self.subtitle_rename()
        self.subtitle_move_best(target_path)
        self.subtitle_move_all(target_path)

    @call_func
    def extract_files(self) -> None:
        log.brackets("Extracting downloads")
        io_file_system.extract_files_in_dir(VIDEO_FILE.tmp_dir, VIDEO_FILE.subs_dir)
        log.task_completed()

    @call_func
    def subtitle_rename(self) -> None:
        log.brackets("Renaming best match")
        new_name = io_file_system.autoload_rename(VIDEO_FILE.filename, ".srt")
        self.autoload_src = new_name

        log.task_completed()

    @call_func
    def subtitle_move_best(self, target: Path) -> None:
        log.brackets("Move best match")
        io_file_system.move_and_replace(self.autoload_src, target)
        log.task_completed()

    @call_func
    def subtitle_move_all(self, target: Path) -> None:
        log.brackets("Move all")
        io_file_system.move_all(VIDEO_FILE.subs_dir, target)
        log.task_completed()

    @call_func
    def summary_notification(self, elapsed) -> None:
        log.brackets("Summary toast")
        elapsed_summary = f"Finished in {elapsed} seconds"
        number_of_results = len(self.accepted_subtitles) + len(self.rejected_subtitles)
        matches_downloaded = f"Downloaded: {self.downloaded_subtitles}/{number_of_results}"
        if self.downloaded_subtitles >= 1:
            msg = "Search Succeeded", f"{matches_downloaded}\n{elapsed_summary}"
            log.stdout(matches_downloaded, hex_color="#a6e3a1")
            self.system_tray.display_toast(*msg)
        elif self.downloaded_subtitles == 0:
            msg = "Search Failed", f"{matches_downloaded}\n{elapsed_summary}"
            log.stdout(matches_downloaded, hex_color="#f38ba8")
            self.system_tray.display_toast(*msg)

    @call_func
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

    def __init__(self, initializer: "Initializer") -> None:
        self.initializer = initializer
        self.sync_state()

    def sync_state(self) -> None:
        self.app_config = self.initializer.app_config
        self.file_exist = self.initializer.file_exist
        self.release_data = self.initializer.release_data
        self.provider_urls = self.initializer.provider_urls
        self.language_data = self.initializer.language_data
        self.accepted_subtitles = self.initializer.accepted_subtitles
        self.rejected_subtitles = self.initializer.rejected_subtitles
        self.downloaded_subtitle_archives = self.initializer.downloaded_subtitle_archives
        self.extracted_subtitle_archives = self.initializer.extracted_subtitle_archives

    def language_supports_provider(self, provider: str) -> bool:
        language = self.app_config.selected_language
        incompatible_providers = self.language_data[language]["incompatibility"]
        return provider not in incompatible_providers

    @property
    def has_accepted(self) -> bool:
        return len(self.accepted_subtitles) >= 1

    @property
    def has_rejected(self) -> bool:
        return len(self.rejected_subtitles) >= 1

    @property
    def should_download_files(self) -> bool:
        if not self.has_accepted:
            return False
        if self.app_config.automatic_downloads:
            return True
        return not self.app_config.always_open_manager and not self.app_config.open_manager_on_no_matches

    @property
    def should_open_download_manager(self) -> bool:
        open_no_matches = not self.has_accepted and self.has_rejected and self.app_config.open_manager_on_no_matches
        always_open = (self.has_accepted or self.has_rejected) and self.app_config.always_open_manager
        return open_no_matches or always_open

    def all_conditions_true(self, conditions: "list[bool | Callable[[], bool]]") -> bool:
        return all(condition() if callable(condition) else condition for condition in conditions)

    def call_func(self, func_name: str) -> bool:
        self.sync_state()
        post_processing = self.app_config.post_processing
        conditions: dict[str, list[bool | Callable[[], bool]]] = {
            "init_search": [self.file_exist],
            "opensubtitles": [
                self.file_exist,
                lambda: self.language_supports_provider("opensubtitles"),
                self.app_config.providers["opensubtitles"],
            ],
            "yifysubtitles": [
                self.file_exist,
                not self.app_config.only_foreign_parts,
                lambda: self.language_supports_provider("yifysubtitles"),
                not self.release_data.tvseries,
                self.provider_urls.yifysubtitles != "",
                self.app_config.providers["yifysubtitles_site"],
            ],
            "subsource": [
                self.file_exist,
                not self.app_config.only_foreign_parts,
                lambda: self.language_supports_provider("subsource"),
                self.app_config.providers["subsource_site"],
            ],
            "download_files": [self.should_download_files],
            "download_manager": [self.should_open_download_manager],
            "subtitle_post_processing": [self.file_exist],
            "extract_files": [self.downloaded_subtitle_archives >= 1],
            "subtitle_rename": [
                self.extracted_subtitle_archives >= 1,
                post_processing["rename"],
            ],
            "subtitle_move_best": [
                self.extracted_subtitle_archives >= 1,
                post_processing["move_best"],
                not post_processing["move_all"],
            ],
            "subtitle_move_all": [
                self.extracted_subtitle_archives >= 1,
                post_processing["move_all"],
            ],
            "summary_notification": [
                self.file_exist,
                self.app_config.summary_notification,
            ],
            "clean_up": [self.file_exist],
        }

        return self.all_conditions_true(conditions[func_name])
