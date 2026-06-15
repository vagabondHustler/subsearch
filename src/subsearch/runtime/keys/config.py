from enum import StrEnum


class ConfigKey(StrEnum):
    LANGUAGE_SELECTED = "language.selected"

    SEARCH_ACCEPT_THRESHOLD = "search.accept_threshold"
    SEARCH_HEARING_IMPAIRED = "search.hearing_impaired"
    SEARCH_NON_HEARING_IMPAIRED = "search.non_hearing_impaired"
    SEARCH_ONLY_FOREIGN_PARTS = "search.only_foreign_parts"
    SEARCH_PROVIDERS = "search.providers"
    SEARCH_DOWNLOADS_PER_PROVIDER = "search.downloads_per_provider"
    SEARCH_TOKEN_WEIGHTS = "search.token_weights"
    SEARCH_TOKEN_MULTIPLIERS = "search.token_multipliers"

    SHELL_INTEGRATION_CONTEXT_MENU = "shell_integration.context_menu"
    SHELL_INTEGRATION_CONTEXT_MENU_ICON = "shell_integration.context_menu_icon"
    SHELL_INTEGRATION_FILE_EXTENSIONS = "shell_integration.file_extensions"

    NOTIFICATIONS_SYSTEM_TRAY = "notifications.system_tray"
    NOTIFICATIONS_SUMMARY_NOTIFICATION = "notifications.summary_notification"

    SUBTITLE_WORKSPACE_SEARCH_MODE = "subtitle_workspace.search_mode"
    SUBTITLE_WORKSPACE_MANUAL_POST_PROCESSING = "subtitle_workspace.manual_post_processing"

    POST_PROCESSING = "post_processing"
    POST_PROCESSING_RENEAME = "post_processing.rename"
    POST_PROCESSING_MOVE_BEST = "post_processing.move_best"
    POST_PROCESSING_MOVE_ALL = "post_processing.move_all"

    PATHS = "paths"
    PATHS_DOWNLOAD_DIRECTORY = "paths.download_directory"
    PATHS_EXTRACTION_DIRECTORY = "paths.extraction_directory"
    PATHS_VIDEO_FILE_DIRECTORY = "paths.video_file_directory"
    PATHS_PATH_RESOLUTION = "paths.path_resolution"
    PATHS_CREATE_MISSING_DIRECTORY = "paths.create_missing_directory"

    APPLICATION_SHOW_TERMINAL = "application.show_terminal"
    APPLICATION_SINGLE_INSTANCE = "application.single_instance"

    NETWORK_REQUEST_CONNECT_TIMEOUT = "network.request_connect_timeout"
    NETWORK_REQUEST_READ_TIMEOUT = "network.request_read_timeout"

    DIAGNOSTICS = "diagnostics"
    DIAGNOSTICS_ENABLED = "diagnostics.enabled"
    DIAGNOSTICS_FAILED_ATTEMPTS_THRESHOLD = "diagnostics.failed_attempts_threshold"

    CREDENTIALS_SUBSOURCE_API_KEY = "credentials.subsource.api_key"
    CREDENTIALS_SUBSOURCE_API_KEY_EXISTS = "credentials.subsource.api_key_exists"
