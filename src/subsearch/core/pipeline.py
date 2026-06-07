import ctypes
import time
from pathlib import Path
from typing import Any, Callable

from subsearch.core.bootstrap import Bootstrap
from subsearch.core.run_conditions import RunConditions
from subsearch.decorators.conditional_execution import run_if_conditions_met
from subsearch.io import file_system
from subsearch.providers import opensubtitles, subsource, yifysubtitles
from subsearch.runtime.config import parallel_tasks
from subsearch.runtime.config.constants import APP_PATHS, DEVICE_INFO, VIDEO_FILE
from subsearch.runtime.logging.logger import log
from subsearch.runtime.models.exceptions import MissingApiKey
from subsearch.runtime.models.model import (
    ProviderHealth,
    ProviderResult,
    SubtitleStatus,
)


class SearchPipeline:
    def __init__(self, pref_counter: float) -> None:
        self.bootstrap = Bootstrap(pref_counter)
        self.call_conditions = RunConditions(self.bootstrap)

        ctypes.windll.kernel32.SetConsoleTitleW(f"subsearch - {DEVICE_INFO.subsearch}")
        if not self.bootstrap.file_exists:
            log.event("banner", title="GUI")
            from subsearch.ui.application import open_settings_window

            open_settings_window()
            log.debug("Exiting GUI")
            self.bootstrap.resync_app_config()
            self.bootstrap.prevent_conflicting_config_settings()
            return None

        if " " in VIDEO_FILE.filename:
            log.warning(f"{VIDEO_FILE.filename} contains spaces, result may vary")

        if not self.bootstrap.all_providers_disabled():
            self.bootstrap.prevent_conflicting_config_settings()
            log.event("banner", title="Search started")

    @run_if_conditions_met
    def init_search(self, *providers: Callable[..., None]) -> None:
        parallel_tasks.run_in_threads(*providers)
        log.event("task_completed")

    @run_if_conditions_met
    def run_provider_diagnostics(self) -> None:
        log.event("banner", title="Provider Healthcheck")
        from subsearch.providers import diagnostics as diagnostics

        diagnostics.record_health_reports(self.bootstrap.health_reports)
        self.bootstrap.resync_app_config()
        self._run_due_diagnostics()

    def _run_due_diagnostics(self) -> None:
        from subsearch.providers import diagnostics as diagnostics

        due_providers = diagnostics.providers_due_for_diagnostic(self.bootstrap.app_config)
        if not due_providers:
            return None
        log.event("banner", title="Provider diagnostics")
        reports = diagnostics.diagnose_providers(due_providers)
        diagnostics.record_health_reports(reports)
        self._notify_unhealthy_providers(reports)
        log.event("task_completed")

    def _notify_unhealthy_providers(self, reports: list[ProviderResult]) -> None:
        unhealthy = [report.provider_name for report in reports if report.health is not ProviderHealth.OK]
        if not unhealthy:
            return None
        message = ", ".join(unhealthy)
        log.warning(f"Provider health check flagged: {message}", color="#f9e2af")
        self.bootstrap.system_tray.display_toast("Provider health", f"May have changed: {message}")

    def _start_search(self, provider: Callable[..., Any], flag: str) -> None:
        search_provider = provider(**self.bootstrap.search_kwargs)
        try:
            search_provider.start_search(flag=flag)
        except MissingApiKey:
            self._notify_missing_api_key(search_provider.provider_name)
        self.bootstrap.accepted_subtitles.extend(search_provider.accepted_subtitles)
        self.bootstrap.rejected_subtitles.extend(search_provider.rejected_subtitles)
        self.bootstrap.health_reports.extend(search_provider.reported_health)

    def _notify_missing_api_key(self, provider_name: str) -> None:
        self.bootstrap.system_tray.display_toast(
            f"{provider_name} skipped",
            "Add your Subsource API key in settings to search Subsource.",
        )

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
        log.event("banner", title=f"Downloading subtitles")
        accepted = sorted(self.bootstrap.accepted_subtitles, key=lambda i: i.percentage_result, reverse=True)
        for subtitle in accepted:
            if subtitle.provider_name not in self.bootstrap.api_calls_made:
                self.bootstrap.api_calls_made[subtitle.provider_name] = 0
            if self.bootstrap.api_calls_made[subtitle.provider_name] == self.bootstrap.app_config.api_call_limit:
                continue
            sub_count = sum(self.bootstrap.api_calls_made.values(), 1)
            index_size = len(accepted)
            file_system.download_subtitle(subtitle, sub_count, index_size)
            subtitle.status = SubtitleStatus.AUTO_DOWNLOADED
            self.bootstrap.api_calls_made[subtitle.provider_name] += 1
        log.event("task_completed")

    @run_if_conditions_met
    def download_manager(self) -> None:
        log.event("banner", title=f"Download Manager")
        subtitles = self.bootstrap.rejected_subtitles + self.bootstrap.accepted_subtitles
        from subsearch.ui.application import open_settings_window

        self.bootstrap.manually_accepted_subtitles = open_settings_window(subtitles)
        self.bootstrap.resync_app_config()
        log.event("task_completed")

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
        log.event("banner", title="Extracting downloads")
        file_system.extract_files_in_dir(VIDEO_FILE.tmp_dir, VIDEO_FILE.subs_dir)
        log.event("task_completed")

    @run_if_conditions_met
    def subtitle_rename(self) -> None:
        log.event("banner", title="Renaming best match")
        new_name = file_system.autoload_rename(VIDEO_FILE.filename, ".srt")
        self.bootstrap.autoload_src = new_name
        log.event("task_completed")

    @run_if_conditions_met
    def subtitle_move_best(self, target: Path) -> None:
        log.event("banner", title="Move best match")
        file_system.move_and_replace(self.bootstrap.autoload_src, target)
        log.event("task_completed")

    @run_if_conditions_met
    def subtitle_move_all(self, target: Path) -> None:
        log.event("banner", title="Move all")
        file_system.move_all(VIDEO_FILE.subs_dir, target)
        log.event("task_completed")

    def _log_provider_health_warnings(self) -> None:
        for report in self.bootstrap.health_reports:
            if report.health is ProviderHealth.STRUCTURE_INVALID:
                log.warning(f"{report.provider_name} may have changed — unrecognized response", color="#f9e2af")

    @run_if_conditions_met
    def summary_notification(self, elapsed) -> None:
        log.event("banner", title="Summary toast")
        self._log_provider_health_warnings()
        elapsed_summary = f"Finished in {elapsed} seconds"
        evaluated = self.bootstrap.accepted_subtitles + self.bootstrap.rejected_subtitles
        downloaded = {
            id(subtitle): subtitle
            for subtitle in evaluated
            if subtitle.status in (SubtitleStatus.AUTO_DOWNLOADED, SubtitleStatus.MANUALLY_DOWNLOADED)
        }
        matches_downloaded = f"Downloaded: {len(downloaded)}/{len(evaluated)}"
        if downloaded:
            msg = "Search Succeeded", f"{matches_downloaded}\n{elapsed_summary}"
            log.info(matches_downloaded, color="#a6e3a1")
            self.bootstrap.system_tray.display_toast(*msg)
        else:
            msg = "Search Failed", f"{matches_downloaded}\n{elapsed_summary}"
            log.info(matches_downloaded, color="#f38ba8")
            self.bootstrap.system_tray.display_toast(*msg)

    @run_if_conditions_met
    def clean_up(self) -> None:
        log.event("banner", title="Cleaning up")
        file_system.del_file_type(VIDEO_FILE.subs_dir, ".nfo")
        file_system.del_directory_content(APP_PATHS.tmp_dir)
        file_system.del_directory(VIDEO_FILE.tmp_dir)
        if file_system.directory_is_empty(VIDEO_FILE.subs_dir):
            file_system.del_directory(VIDEO_FILE.subs_dir)
        log.event("task_completed")

    def on_exit(self) -> None:
        log.event("banner", title="Exit")
        elapsed = time.perf_counter() - self.bootstrap.start
        self.summary_notification(elapsed)
        self.bootstrap.system_tray.stop()
        log.info(f"Finished in {elapsed} seconds", color="#f2cdcd")
        if not self.bootstrap.app_config.show_terminal:
            return None
        if DEVICE_INFO.mode == "executable":
            return None

        try:
            input("Enter to exit")
        except KeyboardInterrupt:
            pass
