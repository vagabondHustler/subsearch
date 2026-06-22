from subsearch.core.pipeline import SearchJob, SearchPipeline
from subsearch.runtime.config import SEARCH_SUBJECT
from subsearch.runtime.logging.events import LogEvent
from subsearch.runtime.logging.logger import log
from subsearch.runtime.models import AppMode, Subtitle


class Flow:
    def __init__(self, pipeline: SearchPipeline) -> None:
        self.pipeline = pipeline
        self.bootstrap = pipeline.bootstrap

    def run(self) -> None:
        raise NotImplementedError

    def _end_initializing(self) -> None:
        return None

    def _record_gui_results(self, manual_accepted: list[Subtitle]) -> None:
        self.bootstrap.manual_accepted_subtitles = manual_accepted
        self.bootstrap.resync_app_config()

    def _finish(self) -> None:
        self.pipeline.subtitle_post_processing()
        log.event(LogEvent.SPINNER, title="Application maintenance", done_title="Application maintenance done")
        self.pipeline.run_provider_diagnostics()
        self.pipeline.present_pending_notifications()
        self.pipeline.clean_up()
        self.pipeline.finish_notification()

    def _make_search_job(self, imdb_id: str = "", tvseries: bool | None = None) -> SearchJob:
        return self.pipeline.create_search_job(imdb_id, tvseries)


class SettingsFlow(Flow):
    def run(self) -> None:
        from subsearch.ui.application import open_settings_window

        manual_accepted = open_settings_window(
            search_job_factory=self._make_search_job,
            on_window_shown=self._end_initializing,
        )
        self._record_gui_results(manual_accepted)
        self._finish()


class ManualSearchFlow(Flow):
    def run(self) -> None:
        from subsearch.ui.application import open_settings_window

        manual_accepted = open_settings_window(
            subtitles=None,
            search_job_factory=self._make_search_job,
            start_search_immediately=True,
            on_window_shown=self._end_initializing,
        )
        self._record_gui_results(manual_accepted)
        self._finish()


_PROVIDER_DISPLAY_NAMES = {
    "opensubtitles": "OpenSubtitles",
    "yifysubtitles_site": "YIFYSubtitles",
    "subsource_site": "Subsource",
    "tvsubtitles_site": "TVsubtitles",
    "gestdown_site": "Gestdown",
}


class PipelineSearchFlow(Flow):
    def run(self) -> None:
        self._end_initializing()
        self._warn_if_filename_has_spaces()
        pipeline = self.pipeline
        log.event(LogEvent.SPINNER, title=self._search_banner(), done_title=self._search_done_banner())
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
        log.event(LogEvent.SPINNER, title="Application maintenance", done_title="Application maintenance done")
        pipeline.run_provider_diagnostics()
        pipeline.present_pending_notifications()
        pipeline.clean_up()
        pipeline.finish_notification()

    def _search_banner(self) -> str:
        if self.bootstrap.all_providers_disabled():
            return "Searching"
        return f"Searching on {self._enabled_provider_names()}"

    def _search_done_banner(self) -> str:
        if self.bootstrap.all_providers_disabled():
            return "Searched"
        return f"Searched on {self._enabled_provider_names()}"

    def _enabled_provider_names(self) -> str:
        providers = self.bootstrap.app_config.providers
        enabled = [name for key, name in _PROVIDER_DISPLAY_NAMES.items() if providers[key]]
        return ", ".join(enabled)

    def _warn_if_filename_has_spaces(self) -> None:
        if " " in SEARCH_SUBJECT.search_term:
            log.event(LogEvent.FLOW_FILENAME_HAS_SPACES, level="warning", filename=SEARCH_SUBJECT.search_term)


FLOW_BY_APP_MODE: dict[AppMode, type[Flow]] = {
    AppMode.SETTINGS: SettingsFlow,
    AppMode.SEARCH_MANUAL: ManualSearchFlow,
    AppMode.SEARCH_HYBRID: PipelineSearchFlow,
    AppMode.SEARCH_AUTOMATIC: PipelineSearchFlow,
}


def create_flow(pipeline: SearchPipeline) -> Flow:
    return FLOW_BY_APP_MODE[pipeline.bootstrap.app_mode](pipeline)
