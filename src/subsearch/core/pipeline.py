import ctypes
import time
from pathlib import Path
from typing import Any, Callable

from subsearch.core import parallel_tasks
from subsearch.core.bootstrap import Bootstrap
from subsearch.core.run_conditions import SKIP_LABEL_EXPLANATIONS, RunConditions
from subsearch.decorators.conditional_execution import run_if_conditions_met
from subsearch.io import file_system
from subsearch.parsing import subtitle_selection
from subsearch.runtime.config import (
    APP_PATHS,
    DEVICE_INFO,
    PATH_RESOLVER,
    SEARCH_SUBJECT,
    WORKSPACE,
)
from subsearch.runtime.models import (
    ProviderDiagnosticStatus,
    ProviderResult,
    SearchOutcome,
    Subtitle,
    SubtitleStatus,
)
from subsearch.runtime.models.exceptions import MissingApiKey
from subsearch.runtime.recorder import LogLevel, capture, get_file_tracker, phase


class SearchJob:
    def __init__(self, pipeline: "SearchPipeline", imdb_id: str = "", tvseries: bool | None = None) -> None:
        self._pipeline = pipeline
        self._imdb_id = imdb_id
        self._tvseries = tvseries

    def execute(self) -> SearchOutcome:
        self._pipeline.bootstrap.ensure_search_mode()
        self._pipeline.bootstrap.resync_app_config()
        capture("Fuzzy matching search inputs")
        self._pipeline.bootstrap.rebuild_search_inputs(self._imdb_id, self._tvseries)
        phase("Searching")
        self._pipeline.init_search(
            self._pipeline.opensubtitles,
            self._pipeline.yifysubtitles,
            self._pipeline.subsource,
            self._pipeline.tvsubtitles,
            self._pipeline.gestdown,
        )
        skipped_providers = self._pipeline.provider_skip_reasons()
        for skip_reason in skipped_providers:
            capture(skip_reason, level=LogLevel.WARNING)
        subtitles = self._pipeline.bootstrap.accepted_subtitles + self._pipeline.bootstrap.rejected_subtitles
        return SearchOutcome(subtitles, skipped_providers)


class SearchPipeline:
    def __init__(self, pref_counter: float) -> None:
        self.bootstrap = Bootstrap(pref_counter)
        self.call_conditions = RunConditions(self.bootstrap)
        self._set_console_title()

    def _set_console_title(self) -> None:
        ctypes.windll.kernel32.SetConsoleTitleW(f"subsearch - {DEVICE_INFO.subsearch}")

    def create_search_job(self, imdb_id: str = "", tvseries: bool | None = None) -> "SearchJob":
        return SearchJob(self, imdb_id, tvseries)

    @run_if_conditions_met
    def init_search(self, *providers: Callable[..., None]) -> None:
        parallel_tasks.run_in_threads(*providers)
        capture("Search completed")

    def provider_skip_reasons(self) -> list[str]:
        reasons = []
        for provider_step in ("opensubtitles", "yifysubtitles", "subsource", "tvsubtitles", "gestdown"):
            unmet_labels = self.call_conditions.unmet_condition_labels(provider_step)
            if not unmet_labels:
                continue
            explanation = "; ".join(SKIP_LABEL_EXPLANATIONS.get(label, label) for label in unmet_labels)
            reasons.append(f"{provider_step} skipped: {explanation}")
        return reasons

    @run_if_conditions_met
    def run_provider_diagnostics(self) -> None:
        from subsearch.providers import diagnostics

        diagnostics.record_health_reports(self.bootstrap.health_reports)
        self.bootstrap.resync_app_config()
        self._run_due_diagnostics()
        capture("Diagnostics completed")

    def _run_due_diagnostics(self) -> None:
        from subsearch.providers import diagnostics

        due_providers = diagnostics.providers_due_for_diagnostic(self.bootstrap.app_config)
        if not due_providers:
            return None
        reports = diagnostics.diagnose_providers(due_providers)
        diagnostics.record_health_reports(reports)
        self._notify_unhealthy_providers(reports)
        capture("Due diagnostics completed")

    def _notify_unhealthy_providers(self, reports: list[ProviderResult]) -> None:
        unhealthy = [
            report.provider_name for report in reports if report.diagnostic_status is not ProviderDiagnosticStatus.OK
        ]
        if not unhealthy:
            return None
        message = ", ".join(unhealthy)
        capture(f"Provider diagnostics flagged: {message}", level=LogLevel.WARNING)
        self.bootstrap.pending_notifications.append(("Provider diagnostics", f"May have changed: {message}"))

    def _start_search(self, provider: Callable[..., Any], flag: str) -> None:
        search_provider = provider(**self.bootstrap.search_kwargs)
        try:
            search_provider.start_search(flag=flag)
        except MissingApiKey:
            self._notify_missing_api_key(search_provider.provider_name)
        self.bootstrap.health_reports.extend(search_provider.reported_health)

    def _notify_missing_api_key(self, provider_name: str) -> None:
        self.bootstrap.pending_notifications.append(
            (
                f"{provider_name} skipped",
                f"Add your {provider_name} API key in settings to search {provider_name}.",
            )
        )

    def present_pending_notifications(self) -> None:
        for title, message in self.bootstrap.pending_notifications:
            self.bootstrap.system_tray.display_toast(title, message)
        self.bootstrap.pending_notifications.clear()

    @run_if_conditions_met
    def opensubtitles(self) -> None:
        from subsearch.providers import opensubtitles

        self._start_search(provider=opensubtitles.OpenSubtitles, flag="site")

    @run_if_conditions_met
    def yifysubtitles(self) -> None:
        from subsearch.providers import yifysubtitles

        self._start_search(provider=yifysubtitles.YifySubtitles, flag="site")

    @run_if_conditions_met
    def subsource(self) -> None:
        from subsearch.providers import subsource

        self._start_search(provider=subsource.Subsource, flag="site")

    @run_if_conditions_met
    def tvsubtitles(self) -> None:
        from subsearch.providers import tvsubtitles

        self._start_search(provider=tvsubtitles.TvSubtitles, flag="site")

    @run_if_conditions_met
    def gestdown(self) -> None:
        from subsearch.providers import gestdown

        self._start_search(provider=gestdown.Gestdown, flag="site")

    def _provider_at_download_limit(self, provider_name: str) -> bool:
        if provider_name not in self.bootstrap.api_calls_made:
            self.bootstrap.api_calls_made[provider_name] = 0
        return self.bootstrap.api_calls_made[provider_name] == self.bootstrap.app_config.downloads_per_provider

    def _download_accepted_subtitle(self, subtitle: Subtitle, total_count: int) -> None:
        subtitle_number = sum(self.bootstrap.api_calls_made.values(), 1)
        downloaded = file_system.download_subtitle(
            subtitle, subtitle_number, total_count, WORKSPACE.download_directory, WORKSPACE.extraction_directory
        )
        subtitle.status = SubtitleStatus.AUTO_DOWNLOAD if downloaded else SubtitleStatus.DOWNLOAD_FAILED
        self.bootstrap.api_calls_made[subtitle.provider_name] += 1

    @run_if_conditions_met
    def download_files(self) -> None:
        phase("Downloading subtitles")
        accepted = sorted(
            self.bootstrap.accepted_subtitles,
            key=lambda subtitle: (subtitle.token_result, subtitle.download_count),
            reverse=True,
        )
        for subtitle in accepted:
            if self._provider_at_download_limit(subtitle.provider_name):
                continue
            self._download_accepted_subtitle(subtitle, len(accepted))
        capture("Downloads completed")

    @run_if_conditions_met
    def subtitle_workspace(self) -> None:
        subtitles = self.bootstrap.rejected_subtitles + self.bootstrap.accepted_subtitles
        from subsearch.ui.entrypoint import open_settings_window

        self.bootstrap.manual_accepted_subtitles = open_settings_window(
            subtitles, search_job_factory=self.create_search_job
        )
        self.bootstrap.resync_app_config()
        capture("Results window closed")

    def _resolve_post_processing_target(self) -> Path:
        return PATH_RESOLVER.resolve_post_processing_target(self.bootstrap.app_config, WORKSPACE.file_directory)

    @run_if_conditions_met
    def subtitle_post_processing(self) -> None:
        phase("Processing subtitles")
        target_path = self._resolve_post_processing_target()
        self.bootstrap.downloaded_subtitle_archives = file_system.count_files_in_directory(WORKSPACE.download_directory)
        self.extract_files()
        self.bootstrap.extracted_subtitle_archives = file_system.count_subtitle_files(WORKSPACE.extraction_directory)
        self.subtitle_rename()
        self.subtitle_move_best(target_path)
        self.subtitle_move_all(target_path)

    @run_if_conditions_met
    def extract_files(self) -> None:
        file_system.extract_files_in_dir(WORKSPACE.download_directory, WORKSPACE.extraction_directory)
        capture("Extraction completed")

    @run_if_conditions_met
    def subtitle_rename(self) -> None:
        new_name = subtitle_selection.autoload_rename(SEARCH_SUBJECT.search_term, WORKSPACE.extraction_directory)
        self.bootstrap.autoload_src = new_name
        capture("Rename completed")

    @run_if_conditions_met
    def subtitle_move_best(self, target: Path) -> None:
        file_system.move_and_replace(self.bootstrap.autoload_src, target)
        capture("Best subtitle moved")

    @run_if_conditions_met
    def subtitle_move_all(self, target: Path) -> None:
        file_system.move_all(WORKSPACE.extraction_directory, target)
        capture("All subtitles moved")

    def _log_provider_diagnostics_warnings(self) -> None:
        for report in self.bootstrap.health_reports:
            if report.diagnostic_status is ProviderDiagnosticStatus.STRUCTURE_INVALID:
                capture(f"{report.provider_name} may have changed, unrecognized response", level=LogLevel.WARNING)

    def _count_downloaded_subtitles(self) -> tuple[int, int]:
        evaluated = self.bootstrap.accepted_subtitles + self.bootstrap.rejected_subtitles
        downloaded = sum(
            1
            for subtitle in evaluated
            if subtitle.status in (SubtitleStatus.AUTO_DOWNLOAD, SubtitleStatus.MANUAL_DOWNLOAD)
        )
        return downloaded, len(evaluated)

    def _dispatch_finish_toast(self, summary_line: str, elapsed_summary: str, succeeded: bool) -> None:
        title = "Search Succeeded" if succeeded else "Search Failed"
        capture(summary_line)
        self.bootstrap.system_tray.display_toast(title, f"{summary_line}\n{elapsed_summary}")

    def _failure_reason(self, total_count: int) -> str:
        if self.bootstrap.all_providers_disabled():
            return "Every provider is disabled in settings"
        reports = self.bootstrap.health_reports
        provider_reports = [report for report in reports if report.provider_name != "imdb"]
        if provider_reports and all(
            report.diagnostic_status is ProviderDiagnosticStatus.NO_RESPONSE for report in provider_reports
        ):
            return "No providers were reachable"
        if any(report.diagnostic_status is ProviderDiagnosticStatus.STRUCTURE_INVALID for report in provider_reports):
            return "A provider's site changed and could not be parsed"
        skipped = self.provider_skip_reasons()
        if skipped and len(skipped) >= len(provider_reports or skipped):
            return "Every provider was skipped for this search"
        if total_count == 0:
            return "No matching subtitles were found"
        return "No subtitles cleared the search threshold"

    @run_if_conditions_met
    def finish_notification(self) -> None:
        self._log_provider_diagnostics_warnings()
        downloaded_count, total_count = self._count_downloaded_subtitles()
        succeeded = downloaded_count > 0
        if succeeded:
            summary_line = "All tasks done!"
        else:
            summary_line = self._failure_reason(total_count)
        elapsed_summary = f"Finished in {self._elapsed()} seconds"
        self._dispatch_finish_toast(summary_line, elapsed_summary, succeeded=succeeded)

    def _elapsed(self) -> float:
        return time.perf_counter() - self.bootstrap.start

    @run_if_conditions_met
    def clean_up(self) -> None:
        file_system.del_directory_content(APP_PATHS.tmp_dir)
        tracker = get_file_tracker()
        if WORKSPACE.download_directory != Path(""):
            tracker.delete_tracked_within(WORKSPACE.extraction_directory, "*.nfo")
            tracker.delete_tracked_within(WORKSPACE.download_directory)
            tracker.delete_if_tracked(WORKSPACE.download_directory)
            if WORKSPACE.extraction_directory.is_dir() and file_system.directory_is_empty(
                WORKSPACE.extraction_directory
            ):
                tracker.delete_if_tracked(WORKSPACE.extraction_directory)
        capture("Cleanup completed")

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
        self.bootstrap.system_tray.stop()
        self._wait_for_terminal_input()
