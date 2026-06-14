import ctypes
import time
from pathlib import Path
from typing import Any, Callable

from subsearch.core.bootstrap import Bootstrap
from subsearch.core.run_conditions import RunConditions
from subsearch.decorators.conditional_execution import run_if_conditions_met
from subsearch.io import file_system, file_tracker
from subsearch.providers import opensubtitles, subsource, yifysubtitles
from subsearch.core import parallel_tasks
from subsearch.runtime.config.constants import APP_PATHS, DEVICE_INFO, VIDEO_FILE
from subsearch.runtime.logging.logger import log
from subsearch.runtime.models.exceptions import MissingApiKey
from subsearch.runtime.models import (
    ProviderDiagnosticStatus,
    ProviderResult,
    SearchOutcome,
    Subtitle,
    SubtitleStatus,
)
from subsearch.ui.state.tasks import Worker

PROVIDER_SKIP_EXPLANATIONS = {
    "provider_enabled": "disabled in settings",
    "language_supports_opensubtitles": "does not support the selected language",
    "language_supports_yifysubtitles": "does not support the selected language",
    "language_supports_subsource": "does not support the selected language",
    "not_only_foreign_parts": "skipped while 'only foreign parts' is enabled",
    "not_tvseries": "does not support tv series",
    "url_not_empty": "needs an IMDb match and none was found for this search",
}


class SearchWorker(Worker):
    def __init__(self, pipeline: "SearchPipeline", imdb_id: str = "") -> None:
        super().__init__()
        self._pipeline = pipeline
        self._imdb_id = imdb_id

    def execute(self) -> SearchOutcome:
        self._pipeline.bootstrap.ensure_search_mode()
        self._pipeline.bootstrap.resync_app_config()
        self._pipeline.bootstrap.rebuild_search_inputs(self._imdb_id)
        self._pipeline.init_search(
            self._pipeline.opensubtitles,
            self._pipeline.yifysubtitles,
            self._pipeline.subsource,
        )
        skipped_providers = self._pipeline.provider_skip_reasons()
        for skip_reason in skipped_providers:
            log.warning(skip_reason)
        subtitles = self._pipeline.bootstrap.accepted_subtitles + self._pipeline.bootstrap.rejected_subtitles
        return SearchOutcome(subtitles, skipped_providers)


class SearchPipeline:
    def __init__(self, pref_counter: float) -> None:
        self.bootstrap = Bootstrap(pref_counter)
        self.call_conditions = RunConditions(self.bootstrap)
        self._set_console_title()

    def _set_console_title(self) -> None:
        ctypes.windll.kernel32.SetConsoleTitleW(f"subsearch - {DEVICE_INFO.subsearch}")

    def _make_search_worker(self, imdb_id: str = "") -> "SearchWorker":
        return SearchWorker(self, imdb_id)

    @run_if_conditions_met
    def init_search(self, *providers: Callable[..., None]) -> None:
        parallel_tasks.run_in_threads(*providers)
        log.event("task_completed")

    def provider_skip_reasons(self) -> list[str]:
        reasons = []
        for provider_step in ("opensubtitles", "yifysubtitles", "subsource"):
            unmet_labels = self.call_conditions.unmet_condition_labels(provider_step)
            if not unmet_labels:
                continue
            explanation = "; ".join(PROVIDER_SKIP_EXPLANATIONS.get(label, label) for label in unmet_labels)
            reasons.append(f"{provider_step} skipped: {explanation}")
        return reasons

    @run_if_conditions_met
    def run_provider_diagnostics(self) -> None:
        log.event("banner", title="Provider diagnostics")
        from subsearch.providers import diagnostics

        diagnostics.record_health_reports(self.bootstrap.health_reports)
        self.bootstrap.resync_app_config()
        self._run_due_diagnostics()
        log.event("task_completed")

    def _run_due_diagnostics(self) -> None:
        from subsearch.providers import diagnostics

        due_providers = diagnostics.providers_due_for_diagnostic(self.bootstrap.app_config)
        if not due_providers:
            return None
        reports = diagnostics.diagnose_providers(due_providers)
        diagnostics.record_health_reports(reports)
        self._notify_unhealthy_providers(reports)
        log.event("task_completed")

    def _notify_unhealthy_providers(self, reports: list[ProviderResult]) -> None:
        unhealthy = [
            report.provider_name for report in reports if report.diagnostic_status is not ProviderDiagnosticStatus.OK
        ]
        if not unhealthy:
            return None
        message = ", ".join(unhealthy)
        log.warning(f"Provider diagnostics flagged: {message}", color="#f9e2af")
        self.bootstrap.system_tray.display_toast("Provider diagnostics", f"May have changed: {message}")

    def _start_search(self, provider: Callable[..., Any], flag: str) -> None:
        search_provider = provider(**self.bootstrap.search_kwargs)
        try:
            search_provider.start_search(flag=flag)
        except MissingApiKey:
            self._notify_missing_api_key(search_provider.provider_name)
        self.bootstrap.health_reports.extend(search_provider.reported_health)

    def _notify_missing_api_key(self, provider_name: str) -> None:
        self.bootstrap.system_tray.display_toast(
            f"{provider_name} skipped",
            f"Add your {provider_name} API key in settings to search {provider_name}.",
        )

    @run_if_conditions_met
    def opensubtitles(self) -> None:
        self._start_search(provider=opensubtitles.OpenSubtitles, flag="site")

    @run_if_conditions_met
    def yifysubtitles(self) -> None:
        self._start_search(provider=yifysubtitles.YifySubtitles, flag="site")

    @run_if_conditions_met
    def subsource(self) -> None:
        self._start_search(provider=subsource.Subsource, flag="site")

    def _provider_at_download_limit(self, provider_name: str) -> bool:
        if provider_name not in self.bootstrap.api_calls_made:
            self.bootstrap.api_calls_made[provider_name] = 0
        return self.bootstrap.api_calls_made[provider_name] == self.bootstrap.app_config.downloads_per_provider

    def _download_accepted_subtitle(self, subtitle: Subtitle, total_count: int) -> None:
        subtitle_number = sum(self.bootstrap.api_calls_made.values(), 1)
        file_system.download_subtitle(subtitle, subtitle_number, total_count, VIDEO_FILE.download_directory)
        subtitle.status = SubtitleStatus.AUTO_DOWNLOADED
        self.bootstrap.api_calls_made[subtitle.provider_name] += 1

    @run_if_conditions_met
    def download_files(self) -> None:
        log.event("banner", title="Downloading subtitles")
        accepted = sorted(self.bootstrap.accepted_subtitles, key=lambda subtitle: subtitle.token_result, reverse=True)
        for subtitle in accepted:
            if self._provider_at_download_limit(subtitle.provider_name):
                continue
            self._download_accepted_subtitle(subtitle, len(accepted))
        log.event("task_completed")

    @run_if_conditions_met
    def download_manager(self) -> None:
        log.event("banner", title="Download Manager")
        subtitles = self.bootstrap.rejected_subtitles + self.bootstrap.accepted_subtitles
        from subsearch.ui.application import open_settings_window

        self.bootstrap.manually_accepted_subtitles = open_settings_window(
            subtitles, search_worker_factory=self._make_search_worker
        )
        self.bootstrap.resync_app_config()
        log.event("task_completed")

    def _resolve_post_processing_target(self) -> Path:
        paths = self.bootstrap.app_config.paths
        target = paths["video_file_directory"]
        resolution = paths["path_resolution"]
        create_missing_directory = paths["create_missing_directory"]
        return file_system.create_path_from_string(
            target, resolution, VIDEO_FILE.file_directory, create_missing_directory
        )

    @run_if_conditions_met
    def subtitle_post_processing(self) -> None:
        target_path = self._resolve_post_processing_target()
        self.bootstrap.downloaded_subtitle_archives = file_system.count_files_in_directory(
            VIDEO_FILE.download_directory
        )
        self.extract_files()
        self.bootstrap.extracted_subtitle_archives = file_system.count_subtitle_files(VIDEO_FILE.extraction_directory)
        self.subtitle_rename()
        self.subtitle_move_best(target_path)
        self.subtitle_move_all(target_path)

    @run_if_conditions_met
    def extract_files(self) -> None:
        log.event("banner", title="Extracting downloads")
        file_system.extract_files_in_dir(VIDEO_FILE.download_directory, VIDEO_FILE.extraction_directory)
        log.event("task_completed")

    @run_if_conditions_met
    def subtitle_rename(self) -> None:
        log.event("banner", title="Renaming best match")
        new_name = file_system.autoload_rename(VIDEO_FILE.filename, VIDEO_FILE.extraction_directory)
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
        file_system.move_all(VIDEO_FILE.extraction_directory, target)
        log.event("task_completed")

    def _log_provider_diagnostics_warnings(self) -> None:
        for report in self.bootstrap.health_reports:
            if report.diagnostic_status is ProviderDiagnosticStatus.STRUCTURE_INVALID:
                log.warning(f"{report.provider_name} may have changed, unrecognized response", color="#f9e2af")

    def _count_downloaded_subtitles(self) -> tuple[int, int]:
        evaluated = self.bootstrap.accepted_subtitles + self.bootstrap.rejected_subtitles
        downloaded = sum(
            1
            for subtitle in evaluated
            if subtitle.status in (SubtitleStatus.AUTO_DOWNLOADED, SubtitleStatus.MANUALLY_DOWNLOADED)
        )
        return downloaded, len(evaluated)

    def _dispatch_summary_toast(self, matches_downloaded: str, elapsed_summary: str, succeeded: bool) -> None:
        title = "Search Succeeded" if succeeded else "Search Failed"
        color = "#a6e3a1" if succeeded else "#f38ba8"
        log.info(matches_downloaded, color=color)
        self.bootstrap.system_tray.display_toast(title, f"{matches_downloaded}\n{elapsed_summary}")

    @run_if_conditions_met
    def summary_notification(self) -> None:
        log.event("banner", title="Summary toast")
        self._log_provider_diagnostics_warnings()
        downloaded_count, total_count = self._count_downloaded_subtitles()
        matches_downloaded = f"Downloaded: {downloaded_count}/{total_count}"
        elapsed_summary = f"Finished in {self._elapsed()} seconds"
        self._dispatch_summary_toast(matches_downloaded, elapsed_summary, succeeded=downloaded_count > 0)

    def _elapsed(self) -> float:
        return time.perf_counter() - self.bootstrap.start

    @run_if_conditions_met
    def clean_up(self) -> None:
        log.event("banner", title="Cleaning up")
        file_system.del_directory_content(APP_PATHS.tmp_dir)
        tracker = file_tracker.get_file_tracker()
        if VIDEO_FILE.download_directory != Path(""):
            tracker.delete_tracked_within(VIDEO_FILE.extraction_directory, "*.nfo")
            tracker.delete_tracked_within(VIDEO_FILE.download_directory)
            tracker.delete_if_tracked(VIDEO_FILE.download_directory)
            if VIDEO_FILE.extraction_directory.is_dir() and file_system.directory_is_empty(
                VIDEO_FILE.extraction_directory
            ):
                tracker.delete_if_tracked(VIDEO_FILE.extraction_directory)
        log.event("task_completed")

    def _wait_for_terminal_input(self) -> None:
        if not self.bootstrap.app_config.show_terminal:
            return None
        if DEVICE_INFO.mode == "executable":
            return None
        try:
            input("Enter to exit")
        except KeyboardInterrupt:
            pass

    def on_exit(self) -> None:
        log.event("banner", title="Exit")
        self.bootstrap.system_tray.stop()
        log.info(f"Finished in {self._elapsed()} seconds", color="#f2cdcd")
        self._wait_for_terminal_input()
