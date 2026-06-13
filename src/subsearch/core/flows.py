from subsearch.core.pipeline import SearchPipeline, SearchWorker
from subsearch.runtime.config.constants import VIDEO_FILE
from subsearch.runtime.logging.logger import log
from subsearch.runtime.models.model import AppMode, Subtitle


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
        self.pipeline.clean_up()

    def _make_search_worker(self, imdb_id: str = "") -> SearchWorker:
        return SearchWorker(self.pipeline, imdb_id)


class SettingsFlow(Flow):
    def run(self) -> None:
        log.event("banner", title="GUI")
        from subsearch.ui.application import open_settings_window

        manually_accepted = open_settings_window(
            search_worker_factory=self._make_search_worker
        )
        log.debug("Exiting GUI")
        self._record_gui_results(manually_accepted)
        self.bootstrap.prevent_conflicting_config_settings()
        self._finish()


class ManualSearchFlow(Flow):
    def run(self) -> None:
        log.event("banner", title="Download Manager")
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
        log.event("banner", title="Download Manager")
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


class PipelineSearchFlow(Flow):
    def run(self) -> None:
        self._warn_if_filename_has_spaces()
        if not self.bootstrap.all_providers_disabled():
            self.bootstrap.prevent_conflicting_config_settings()
            log.event("banner", title="Search started")
        pipeline = self.pipeline
        pipeline.init_search(pipeline.opensubtitles, pipeline.yifysubtitles, pipeline.subsource)
        pipeline.download_files()
        pipeline.download_manager()
        self._finish()

    def _warn_if_filename_has_spaces(self) -> None:
        if " " in VIDEO_FILE.filename:
            log.warning(f"{VIDEO_FILE.filename} contains spaces, result may vary")


FLOW_BY_APP_MODE: dict[AppMode, type[Flow]] = {
    AppMode.SETTINGS: SettingsFlow,
    AppMode.SEARCH_MANUAL: ManualSearchFlow,
    AppMode.DEV: DevPreviewFlow,
    AppMode.SEARCH_HYBRID: PipelineSearchFlow,
    AppMode.SEARCH_AUTOMATIC: PipelineSearchFlow,
}


def create_flow(pipeline: SearchPipeline) -> Flow:
    return FLOW_BY_APP_MODE[pipeline.bootstrap.app_mode](pipeline)
