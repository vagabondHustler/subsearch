import ctypes
import time
from pathlib import Path
from typing import Any, Callable

from subsearch import threading_utils, ui
from subsearch.bootstrap import Bootstrap
from subsearch.decorators.conditional_execution import run_if_conditions_met
from subsearch.io import file_system
from subsearch.logger import log
from subsearch.model import Subtitle
from subsearch.providers import opensubtitles, subsource, yifysubtitles
from subsearch.run_conditions import RunConditions
from subsearch.runtime.constants import APP_PATHS, DEVICE_INFO, VIDEO_FILE


class SearchPipeline:
    def __init__(self, pref_counter: float) -> None:
        self.bootstrap = Bootstrap(pref_counter)
        self.call_conditions = RunConditions(self.bootstrap)

        ctypes.windll.kernel32.SetConsoleTitleW(f"subsearch - {DEVICE_INFO.subsearch}")
        if not self.bootstrap.file_exist:
            log.brackets("GUI")
            ui.open_settings_window()
            log.stdout("Exiting GUI", level="debug")
            self.bootstrap.prevent_conflicting_config_settings()
            return None

        if " " in VIDEO_FILE.filename:
            log.stdout(f"{VIDEO_FILE.filename} contains spaces, result may vary", level="warning")

        if not self.bootstrap.all_providers_disabled():
            self.bootstrap.prevent_conflicting_config_settings()
            log.brackets("Search started")

    @run_if_conditions_met
    def init_search(self, *providers: Callable[..., None]) -> None:
        threading_utils.run_in_threads(*providers)
        log.task_completed()

    def _start_search(self, provider: Callable[..., Any], flag: str) -> None:
        search_provider = provider(**self.bootstrap.search_kwargs)
        search_provider.start_search(flag=flag)
        self.bootstrap.accepted_subtitles.extend(search_provider.accepted_subtitles)
        self.bootstrap.rejected_subtitles.extend(search_provider.rejected_subtitles)

    @run_if_conditions_met
    def opensubtitles(self) -> None:
        self._start_search(provider=opensubtitles.OpenSubtitles, flag="site")

    @run_if_conditions_met
    def yifysubtitles(self) -> None:
        self._start_search(provider=yifysubtitles.YifiSubtitles, flag="site")

    @run_if_conditions_met
    def subsource(self) -> None:
        self._start_search(provider=subsource.Subsource, flag="site")

    @run_if_conditions_met
    def download_files(self) -> None:
        log.brackets(f"Downloading subtitles")
        accepted = sorted(self.bootstrap.accepted_subtitles, key=lambda i: i.precentage_result, reverse=True)
        keep: list[Subtitle] = []
        for subtitle in accepted:
            if subtitle.provider_name not in self.bootstrap.api_calls_made:
                self.bootstrap.api_calls_made[subtitle.provider_name] = 0
            if self.bootstrap.api_calls_made[subtitle.provider_name] == self.bootstrap.app_config.api_call_limit:
                self.bootstrap.rejected_subtitles.append(subtitle)
                continue
            if subtitle.provider_name == "subsource":
                resolved = self._handle_subsource_subtitle(subtitle)
                if resolved is None:
                    continue
                subtitle = resolved
            sub_count = sum(self.bootstrap.api_calls_made.values(), 1)
            index_size = len(accepted)
            file_system.download_subtitle(subtitle, sub_count, index_size)
            self.bootstrap.downloaded_subtitles += 1
            self.bootstrap.api_calls_made[subtitle.provider_name] += 1
            keep.append(subtitle)
        self.bootstrap.accepted_subtitles = keep
        log.task_completed()

    def _handle_subsource_subtitle(self, subtitle: Subtitle) -> Subtitle | None:
        if not self.bootstrap.app_config.providers["subsource_site"]:
            return subtitle
        subsource_api = subsource.GetDownloadUrl()
        download_url = subsource_api.get_url(subtitle)
        if not download_url:
            log.stdout(f"{subtitle.provider_name} could not be reached. Removed {subtitle.subtitle_name}")
            return None
        subtitle.download_url = download_url
        subtitle.request_data = {}
        return subtitle

    @run_if_conditions_met
    def download_manager(self) -> None:
        log.brackets(f"Download Manager")
        subtitles = self.bootstrap.rejected_subtitles + self.bootstrap.accepted_subtitles
        self.bootstrap.manually_accepted_subtitles = ui.open_settings_window(subtitles)
        self.bootstrap.downloaded_subtitles += len(self.bootstrap.manually_accepted_subtitles)
        log.task_completed()

    @run_if_conditions_met
    def subtitle_post_processing(self) -> None:
        target = self.bootstrap.app_config.post_processing["target_path"]
        resolution = self.bootstrap.app_config.post_processing["path_resolution"]
        create_missing_folder = self.bootstrap.app_config.post_processing["create_missing_folder"]
        target_path = file_system.create_path_from_string(target, resolution, create_missing_folder)
        self.bootstrap.downloaded_subtitle_archives = file_system.count_files_in_directory(VIDEO_FILE.tmp_dir)
        self.extract_files()
        self.bootstrap.extracted_subtitle_archives = file_system.count_files_in_directory(VIDEO_FILE.subs_dir, [".srt"])
        self.subtitle_rename()
        self.subtitle_move_best(target_path)
        self.subtitle_move_all(target_path)

    @run_if_conditions_met
    def extract_files(self) -> None:
        log.brackets("Extracting downloads")
        file_system.extract_files_in_dir(VIDEO_FILE.tmp_dir, VIDEO_FILE.subs_dir)
        log.task_completed()

    @run_if_conditions_met
    def subtitle_rename(self) -> None:
        log.brackets("Renaming best match")
        new_name = file_system.autoload_rename(VIDEO_FILE.filename, ".srt")
        self.bootstrap.autoload_src = new_name
        log.task_completed()

    @run_if_conditions_met
    def subtitle_move_best(self, target: Path) -> None:
        log.brackets("Move best match")
        file_system.move_and_replace(self.bootstrap.autoload_src, target)
        log.task_completed()

    @run_if_conditions_met
    def subtitle_move_all(self, target: Path) -> None:
        log.brackets("Move all")
        file_system.move_all(VIDEO_FILE.subs_dir, target)
        log.task_completed()

    @run_if_conditions_met
    def summary_notification(self, elapsed) -> None:
        log.brackets("Summary toast")
        elapsed_summary = f"Finished in {elapsed} seconds"
        number_of_results = len(self.bootstrap.accepted_subtitles) + len(self.bootstrap.rejected_subtitles)
        matches_downloaded = f"Downloaded: {self.bootstrap.downloaded_subtitles}/{number_of_results}"
        if self.bootstrap.downloaded_subtitles >= 1:
            msg = "Search Succeeded", f"{matches_downloaded}\n{elapsed_summary}"
            log.stdout(matches_downloaded, hex_color="#a6e3a1")
            self.bootstrap.system_tray.display_toast(*msg)
        elif self.bootstrap.downloaded_subtitles == 0:
            msg = "Search Failed", f"{matches_downloaded}\n{elapsed_summary}"
            log.stdout(matches_downloaded, hex_color="#f38ba8")
            self.bootstrap.system_tray.display_toast(*msg)

    @run_if_conditions_met
    def clean_up(self) -> None:
        log.brackets("Cleaning up")
        file_system.del_file_type(VIDEO_FILE.subs_dir, ".nfo")
        file_system.del_directory_content(APP_PATHS.tmp_dir)
        file_system.del_directory(VIDEO_FILE.tmp_dir)
        if file_system.directory_is_empty(VIDEO_FILE.subs_dir):
            file_system.del_directory(VIDEO_FILE.subs_dir)
        log.task_completed()

    def on_exit(self) -> None:
        log.brackets("Exit")
        elapsed = time.perf_counter() - self.bootstrap.start
        self.summary_notification(elapsed)
        self.bootstrap.system_tray.stop()
        log.stdout(f"Finished in {elapsed} seconds", hex_color="#f2cdcd")
        if not self.bootstrap.app_config.show_terminal:
            return None
        if DEVICE_INFO.mode == "executable":
            return None

        try:
            input("Enter to exit")
        except KeyboardInterrupt:
            pass
