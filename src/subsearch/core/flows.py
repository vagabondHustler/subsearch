from subsearch.core.pipeline import SearchJob, SearchPipeline
from subsearch.runtime.config import PROVIDER_DISPLAY_NAMES, SEARCH_SUBJECT
from subsearch.runtime.models import AppMode, WorkspaceOutcome
from subsearch.runtime.recorder import LogLevel, capture, phase


class Flow:
    def __init__(self, pipeline: SearchPipeline) -> None:
        self.pipeline = pipeline
        self.bootstrap = pipeline.bootstrap

    def run(self) -> None:
        raise NotImplementedError

    def _end_initializing(self) -> None:
        return None

    def _record_gui_results(self, outcome: WorkspaceOutcome) -> None:
        self.bootstrap.manual_accepted_subtitles = outcome.downloaded
        self.bootstrap.ui_placed_best_next_to_video = outcome.placed_best_next_to_video
        self.bootstrap.resync_app_config()

    def _finish(self) -> None:
        self.pipeline.subtitle_post_processing()
        phase("Application maintenance")
        self.pipeline.run_provider_diagnostics()
        self.pipeline.present_pending_notifications()
        self.pipeline.clean_up()
        self.pipeline.finish_notification()

    def _make_search_job(self, imdb_id: str = "", tvseries: bool | None = None) -> SearchJob:
        return self.pipeline.create_search_job(imdb_id, tvseries)


class SettingsFlow(Flow):
    def run(self) -> None:
        from subsearch.ui.entrypoint import open_settings_window

        outcome = open_settings_window(
            search_job_factory=self._make_search_job,
            on_window_shown=self._end_initializing,
        )
        self._record_gui_results(outcome)
        self._finish()


class ManualSearchFlow(Flow):
    def run(self) -> None:
        from subsearch.ui.entrypoint import open_settings_window

        outcome = open_settings_window(
            subtitles=None,
            search_job_factory=self._make_search_job,
            start_search_immediately=True,
            on_window_shown=self._end_initializing,
        )
        self._record_gui_results(outcome)
        self._finish()


class PipelineSearchFlow(Flow):
    def run(self) -> None:
        self._end_initializing()
        self._warn_if_filename_has_spaces()
        pipeline = self.pipeline
        phase(self._search_banner())
        pipeline.init_search(
            pipeline.opensubtitles,
            pipeline.yifysubtitles,
            pipeline.subsource,
            pipeline.tvsubtitles,
            pipeline.gestdown,
        )
        pipeline.subtitle_workspace()
        pipeline.download_files()
        pipeline.subtitle_post_processing()
        phase("Application maintenance")
        pipeline.run_provider_diagnostics()
        pipeline.present_pending_notifications()
        pipeline.clean_up()
        pipeline.finish_notification()

    def _search_banner(self) -> str:
        if self.bootstrap.all_providers_disabled():
            return "Searching"
        return f"Searching on {self._enabled_provider_names()}"

    def _enabled_provider_names(self) -> str:
        providers = self.bootstrap.app_config.providers
        enabled = [name for key, name in PROVIDER_DISPLAY_NAMES.items() if providers[key]]
        return ", ".join(enabled)

    def _warn_if_filename_has_spaces(self) -> None:
        if " " in SEARCH_SUBJECT.search_term:
            capture(f"{SEARCH_SUBJECT.search_term} contains spaces, result may vary", level=LogLevel.WARNING)


FLOW_BY_APP_MODE: dict[AppMode, type[Flow]] = {
    AppMode.SETTINGS: SettingsFlow,
    AppMode.SEARCH_MANUAL: ManualSearchFlow,
    AppMode.SEARCH_HYBRID: PipelineSearchFlow,
    AppMode.SEARCH_AUTOMATIC: PipelineSearchFlow,
}


def create_flow(pipeline: SearchPipeline) -> Flow:
    return FLOW_BY_APP_MODE[pipeline.bootstrap.app_mode](pipeline)
