from enum import StrEnum


class PipelineStep(StrEnum):
    INIT_SEARCH = "init_search"
    OPENSUBTITLES = "opensubtitles"
    YIFYSUBTITLES = "yifysubtitles"
    SUBSOURCE = "subsource"
    DOWNLOAD_FILES = "download_files"
    SUBTITLE_WORKSPACE = "subtitle_workspace"
    SUBTITLE_POST_PROCESSING = "subtitle_post_processing"
    EXTRACT_FILES = "extract_files"
    SUBTITLE_RENAME = "subtitle_rename"
    SUBTITLE_MOVE_BEST = "subtitle_move_best"
    SUBTITLE_MOVE_ALL = "subtitle_move_all"
    SUMMARY_NOTIFICATION = "summary_notification"
    RUN_PROVIDER_DIAGNOSTICS = "run_provider_diagnostics"
    CLEAN_UP = "clean_up"
