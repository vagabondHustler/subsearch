from subsearch.core.pipeline import SearchPipeline, SearchWorker
from subsearch.runtime.config import SEARCH_SUBJECT
from subsearch.runtime.logging.logger import log
from subsearch.runtime.models import AppMode, Subtitle


class Flow:
    def __init__(self, pipeline: SearchPipeline) -> None:
        self.pipeline = pipeline
        self.bootstrap = pipeline.bootstrap

    def run(self) -> None:
        raise NotImplementedError

    def _record_gui_results(self, manually_accepted: list[Subtitle]) -> None:
        self.bootstrap.manually_accepted_subtitles = manually_accepted
        self.bootstrap.resync_app_config()

    def _finish(self) -> None:
        self.pipeline.subtitle_post_processing()
        self.pipeline.run_provider_diagnostics()
        self.pipeline.summary_notification()
        self.pipeline.clean_up()

    def _make_search_worker(self, imdb_id: str = "") -> SearchWorker:
        return SearchWorker(self.pipeline, imdb_id)


class SettingsFlow(Flow):
    def run(self) -> None:
        log.event("banner", title="Opening UI")
        from subsearch.ui.application import open_settings_window

        manually_accepted = open_settings_window(search_worker_factory=self._make_search_worker)
        self._record_gui_results(manually_accepted)
        self._finish()


class ManualSearchFlow(Flow):
    def run(self) -> None:
        log.event("banner", title="Presenting results")
        from subsearch.ui.application import open_settings_window

        manually_accepted = open_settings_window(
            subtitles=None,
            search_worker_factory=self._make_search_worker,
            start_search_immediately=True,
        )
        self._record_gui_results(manually_accepted)
        log.event("task_completed")
        self._finish()


class DevPreviewFlow(Flow):
    def run(self) -> None:
        log.event("banner", title="Presenting results")
        from subsearch.ui.application import open_settings_window
        from subsearch.ui.services.dev_stubs import (
            DevPostProcessingService,
            DevSearchWorker,
            DevSubtitleDownloadService,
        )

        manually_accepted = open_settings_window(
            subtitles=None,
            search_worker_factory=DevSearchWorker,
            download_service=DevSubtitleDownloadService(),
            post_processing_service=DevPostProcessingService(),
            start_search_immediately=True,
        )
        self._record_gui_results(manually_accepted)
        log.event("task_completed")
        self._finish()


_PROVIDER_DISPLAY_NAMES = {
    "opensubtitles": "OpenSubtitles",
    "yifysubtitles_site": "YIFYSubtitles",
    "subsource_site": "Subsource",
}


class PipelineSearchFlow(Flow):
    def run(self) -> None:
        self._warn_if_filename_has_spaces()
        if not self.bootstrap.all_providers_disabled():
            log.event("banner", title=f"Searching on {self._enabled_provider_names()}")
        pipeline = self.pipeline
        pipeline.init_search(pipeline.opensubtitles, pipeline.yifysubtitles, pipeline.subsource)
        pipeline.download_files()
        pipeline.download_manager()
        self._finish()

    def _enabled_provider_names(self) -> str:
        providers = self.bootstrap.app_config.providers
        enabled = [name for key, name in _PROVIDER_DISPLAY_NAMES.items() if providers[key]]
        return ", ".join(enabled)

    def _warn_if_filename_has_spaces(self) -> None:
        if " " in SEARCH_SUBJECT.search_term:
            log.event("flow.filename_has_spaces", level="warning", filename=SEARCH_SUBJECT.search_term)


FLOW_BY_APP_MODE: dict[AppMode, type[Flow]] = {
    AppMode.SETTINGS: SettingsFlow,
    AppMode.SEARCH_MANUAL: ManualSearchFlow,
    AppMode.DEV: DevPreviewFlow,
    AppMode.SEARCH_HYBRID: PipelineSearchFlow,
    AppMode.SEARCH_AUTOMATIC: PipelineSearchFlow,
}


def create_flow(pipeline: SearchPipeline) -> Flow:
    return FLOW_BY_APP_MODE[pipeline.bootstrap.app_mode](pipeline)
