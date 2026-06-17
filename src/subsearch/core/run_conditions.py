from enum import StrEnum
from typing import Callable

from subsearch.core.bootstrap import Bootstrap
from subsearch.runtime.logging.events import LogEvent
from subsearch.runtime.logging.logger import log
from subsearch.runtime.models import AppMode


class PipelineStep(StrEnum):
    INIT_SEARCH = "init_search"
    OPENSUBTITLES = "opensubtitles"
    YIFYSUBTITLES = "yifysubtitles"
    SUBSOURCE = "subsource"
    TVSUBTITLES = "tvsubtitles"
    GESTDOWN = "gestdown"
    DOWNLOAD_FILES = "download_files"
    SUBTITLE_WORKSPACE = "subtitle_workspace"
    SUBTITLE_POST_PROCESSING = "subtitle_post_processing"
    EXTRACT_FILES = "extract_files"
    SUBTITLE_RENAME = "subtitle_rename"
    SUBTITLE_MOVE_BEST = "subtitle_move_best"
    SUBTITLE_MOVE_ALL = "subtitle_move_all"
    FINISH_NOTIFICATION = "finish_notification"
    RUN_PROVIDER_DIAGNOSTICS = "run_provider_diagnostics"
    CLEAN_UP = "clean_up"


ConditionList = list[tuple[str, "bool | Callable[[], bool]"]]


class RunConditions:
    def __init__(self, bootstrap: Bootstrap) -> None:
        self.bootstrap = bootstrap
        self.sync_state()

    def sync_state(self) -> None:
        self.app_config = self.bootstrap.app_config
        self.app_mode = self.bootstrap.app_mode
        self.release_data = self.bootstrap.release_data
        self.provider_urls = self.bootstrap.provider_urls
        self.language_data = self.bootstrap.language_data
        self.accepted_subtitles = self.bootstrap.accepted_subtitles
        self.rejected_subtitles = self.bootstrap.rejected_subtitles
        self.downloaded_subtitle_archives = self.bootstrap.downloaded_subtitle_archives
        self.extracted_subtitle_archives = self.bootstrap.extracted_subtitle_archives

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
    def manual_post_processing(self) -> bool:
        if not self.should_open_subtitle_workspace:
            return False
        return self.app_config.subtitle_workspace_manual_post_processing

    @property
    def is_search_mode(self) -> bool:
        return self.app_mode in (
            AppMode.SEARCH_MANUAL,
            AppMode.SEARCH_HYBRID,
            AppMode.SEARCH_AUTOMATIC,
        )

    @property
    def is_pipeline_post_processing_mode(self) -> bool:
        return self.app_mode in (AppMode.SEARCH_HYBRID, AppMode.SEARCH_AUTOMATIC)

    @property
    def should_download_files(self) -> bool:
        if not self.has_accepted:
            return False
        if self.app_mode is AppMode.SEARCH_AUTOMATIC:
            return True
        if self.app_mode is AppMode.SEARCH_HYBRID:
            return True
        return False

    @property
    def should_open_subtitle_workspace(self) -> bool:
        if self.app_mode is AppMode.SEARCH_MANUAL:
            return True
        if self.app_mode is AppMode.SEARCH_HYBRID and not self.has_accepted:
            return True
        return False

    def _evaluate_and_log(self, pipeline_step: PipelineStep | str, condition_list: ConditionList) -> bool:
        results = [(label, condition() if callable(condition) else condition) for label, condition in condition_list]
        passed = all(value for _, value in results)
        detail = ", ".join(f"{label}={value}" for label, value in results)
        log.event(
            LogEvent.RUN_CONDITIONS_EVALUATED,
            level="debug",
            step=pipeline_step,
            detail=detail,
            decision="run" if passed else "skip",
        )
        return passed

    def conditions_met(self, pipeline_step: PipelineStep | str) -> bool:
        self.sync_state()
        return self._evaluate_and_log(pipeline_step, self._conditions_for(pipeline_step))

    def unmet_condition_labels(self, pipeline_step: PipelineStep | str) -> list[str]:
        self.sync_state()
        return [
            label
            for label, condition in self._conditions_for(pipeline_step)
            if not (condition() if callable(condition) else condition)
        ]

    def _conditions_for(self, pipeline_step: PipelineStep | str) -> ConditionList:
        post_processing = self.app_config.post_processing
        not_manual_handled = ("not_manual_post_processing", not self.manual_post_processing)
        conditions: dict[PipelineStep, ConditionList] = {
            PipelineStep.INIT_SEARCH: [
                ("app_mode_search", self.is_search_mode),
            ],
            PipelineStep.OPENSUBTITLES: [
                ("language_supports_opensubtitles", lambda: self.language_supports_provider("opensubtitles")),
                ("provider_enabled", self.app_config.providers["opensubtitles"]),
            ],
            PipelineStep.YIFYSUBTITLES: [
                ("not_only_foreign_parts", not self.app_config.only_foreign_parts),
                ("language_supports_yifysubtitles", lambda: self.language_supports_provider("yifysubtitles")),
                ("not_tvseries", not self.release_data.tvseries),
                ("url_not_empty", len(self.provider_urls.yifysubtitles) > 0),
                ("provider_enabled", self.app_config.providers["yifysubtitles_site"]),
            ],
            PipelineStep.SUBSOURCE: [
                ("not_only_foreign_parts", not self.app_config.only_foreign_parts),
                ("language_supports_subsource", lambda: self.language_supports_provider("subsource")),
                ("provider_enabled", self.app_config.providers["subsource_site"]),
            ],
            PipelineStep.TVSUBTITLES: [
                ("not_only_foreign_parts", not self.app_config.only_foreign_parts),
                ("language_supports_tvsubtitles", lambda: self.language_supports_provider("tvsubtitles")),
                ("is_tvseries", self.release_data.tvseries),
                ("url_not_empty", len(self.provider_urls.tvsubtitles) > 0),
                ("provider_enabled", self.app_config.providers["tvsubtitles_site"]),
            ],
            PipelineStep.GESTDOWN: [
                ("not_only_foreign_parts", not self.app_config.only_foreign_parts),
                ("language_supports_gestdown", lambda: self.language_supports_provider("gestdown")),
                ("is_tvseries", self.release_data.tvseries),
                ("provider_enabled", self.app_config.providers["gestdown_site"]),
            ],
            PipelineStep.DOWNLOAD_FILES: [
                not_manual_handled,
                ("should_download_files", self.should_download_files),
            ],
            PipelineStep.SUBTITLE_WORKSPACE: [
                ("should_open_subtitle_workspace", self.should_open_subtitle_workspace),
            ],
            PipelineStep.SUBTITLE_POST_PROCESSING: [
                not_manual_handled,
                ("app_mode_pipeline_post_processing", self.is_pipeline_post_processing_mode),
            ],
            PipelineStep.EXTRACT_FILES: [
                not_manual_handled,
                ("app_mode_pipeline_post_processing", self.is_pipeline_post_processing_mode),
                ("downloaded_archives_gte_1", self.downloaded_subtitle_archives >= 1),
            ],
            PipelineStep.SUBTITLE_RENAME: [
                not_manual_handled,
                ("app_mode_pipeline_post_processing", self.is_pipeline_post_processing_mode),
                ("extracted_archives_gte_1", self.extracted_subtitle_archives >= 1),
                ("rename_enabled", post_processing["rename"]),
            ],
            PipelineStep.SUBTITLE_MOVE_BEST: [
                not_manual_handled,
                ("app_mode_pipeline_post_processing", self.is_pipeline_post_processing_mode),
                ("extracted_archives_gte_1", self.extracted_subtitle_archives >= 1),
                ("move_best_enabled", post_processing["move_best"]),
                ("not_move_all", not post_processing["move_all"]),
            ],
            PipelineStep.SUBTITLE_MOVE_ALL: [
                not_manual_handled,
                ("app_mode_pipeline_post_processing", self.is_pipeline_post_processing_mode),
                ("extracted_archives_gte_1", self.extracted_subtitle_archives >= 1),
                ("move_all_enabled", post_processing["move_all"]),
            ],
            PipelineStep.FINISH_NOTIFICATION: [
                ("app_mode_search", self.is_search_mode),
            ],
            PipelineStep.RUN_PROVIDER_DIAGNOSTICS: [
                ("app_mode_search", self.is_search_mode),
                ("diagnostics_enabled", self.app_config.diagnostics["enabled"]),
            ],
            PipelineStep.CLEAN_UP: [],
        }

        return conditions[PipelineStep(pipeline_step)]
