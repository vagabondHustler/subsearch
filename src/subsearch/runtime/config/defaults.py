from enum import StrEnum
from typing import Any

from subsearch.runtime.config.nested_dict import insert_nested_value


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
    NOTIFICATIONS_DISPLAY_DURATION = "notifications.display_duration"
    NOTIFICATIONS_PLAY_SOUND = "notifications.play_sound"

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
    APPLICATION_SHOW_TRAY_ICON = "application.show_tray_icon"
    APPLICATION_SINGLE_INSTANCE = "application.single_instance"

    NETWORK_REQUEST_CONNECT_TIMEOUT = "network.request_connect_timeout"
    NETWORK_REQUEST_READ_TIMEOUT = "network.request_read_timeout"

    DIAGNOSTICS = "diagnostics"
    DIAGNOSTICS_ENABLED = "diagnostics.enabled"
    DIAGNOSTICS_FAILED_ATTEMPTS_THRESHOLD = "diagnostics.failed_attempts_threshold"

    CREDENTIALS_SUBSOURCE_API_KEY = "credentials.subsource.api_key"
    CREDENTIALS_SUBSOURCE_API_KEY_EXISTS = "credentials.subsource.api_key_exists"


SUPPORTED_FILE_EXTENSIONS: list[str] = [
    "avi",
    "mp4",
    "mkv",
    "mpg",
    "mpeg",
    "mov",
    "rm",
    "vob",
    "wmv",
    "flv",
    "3gp",
    "3g2",
    "swf",
    "mswmm",
]

DEFAULT_TOKEN_WEIGHTS: dict[str, float] = {
    "title": 75,
    "group": 5,
    "source": 20,
}

DEFAULT_TOKEN_MULTIPLIERS: dict[str, float] = {
    "year": 0.1,
    "season_episode": 0.1,
    "edition": 0.1,
}

SUPPORTED_PROVIDERS: list[str] = [
    "opensubtitles",
    "yifysubtitles_site",
    "subsource_site",
    "tvsubtitles_site",
    "gestdown_site",
]

HEALTH_TRACKED_PROVIDERS: list[str] = [
    "imdb",
    "opensubtitles",
    "yifysubtitles",
    "subsource",
    "tvsubtitles",
    "gestdown",
]

# Per-provider runtime health counters Subsearch manages itself. They live under a section
# with no single ConfigKey, so they are seeded by their dotted path rather than the enum.
UNKEYED_PROVIDER_DIAGNOSTICS = "diagnostics.provider_diagnostics"


def get_default_app_config() -> dict[str, Any]:
    defaults: dict[ConfigKey, Any] = {
        ConfigKey.LANGUAGE_SELECTED: "english",
        ConfigKey.SEARCH_ACCEPT_THRESHOLD: 90,
        ConfigKey.SEARCH_HEARING_IMPAIRED: True,
        ConfigKey.SEARCH_NON_HEARING_IMPAIRED: True,
        ConfigKey.SEARCH_ONLY_FOREIGN_PARTS: False,
        ConfigKey.SEARCH_PROVIDERS: dict.fromkeys(SUPPORTED_PROVIDERS, True),
        ConfigKey.SEARCH_DOWNLOADS_PER_PROVIDER: 4,
        ConfigKey.SEARCH_TOKEN_WEIGHTS: {**DEFAULT_TOKEN_WEIGHTS},
        ConfigKey.SEARCH_TOKEN_MULTIPLIERS: {**DEFAULT_TOKEN_MULTIPLIERS},
        ConfigKey.SHELL_INTEGRATION_CONTEXT_MENU: True,
        ConfigKey.SHELL_INTEGRATION_CONTEXT_MENU_ICON: True,
        ConfigKey.SHELL_INTEGRATION_FILE_EXTENSIONS: dict.fromkeys(SUPPORTED_FILE_EXTENSIONS, True),
        ConfigKey.NOTIFICATIONS_SYSTEM_TRAY: True,
        ConfigKey.NOTIFICATIONS_DISPLAY_DURATION: 3.5,
        ConfigKey.NOTIFICATIONS_PLAY_SOUND: True,
        ConfigKey.SUBTITLE_WORKSPACE_SEARCH_MODE: "hybrid",
        ConfigKey.SUBTITLE_WORKSPACE_MANUAL_POST_PROCESSING: False,
        ConfigKey.POST_PROCESSING_RENEAME: True,
        ConfigKey.POST_PROCESSING_MOVE_BEST: True,
        ConfigKey.POST_PROCESSING_MOVE_ALL: False,
        ConfigKey.PATHS_DOWNLOAD_DIRECTORY: "",
        ConfigKey.PATHS_EXTRACTION_DIRECTORY: "",
        ConfigKey.PATHS_VIDEO_FILE_DIRECTORY: ".",
        ConfigKey.PATHS_PATH_RESOLUTION: "relative",
        ConfigKey.PATHS_CREATE_MISSING_DIRECTORY: True,
        ConfigKey.APPLICATION_SHOW_TERMINAL: False,
        ConfigKey.APPLICATION_SHOW_TRAY_ICON: True,
        ConfigKey.APPLICATION_SINGLE_INSTANCE: True,
        ConfigKey.NETWORK_REQUEST_CONNECT_TIMEOUT: 4,
        ConfigKey.NETWORK_REQUEST_READ_TIMEOUT: 5,
        ConfigKey.DIAGNOSTICS_ENABLED: True,
        ConfigKey.DIAGNOSTICS_FAILED_ATTEMPTS_THRESHOLD: 3,
        ConfigKey.CREDENTIALS_SUBSOURCE_API_KEY_EXISTS: False,
        ConfigKey.CREDENTIALS_SUBSOURCE_API_KEY: "",
    }

    config: dict[str, Any] = {}
    for config_key, default_value in defaults.items():
        insert_nested_value(config, config_key, default_value)

    provider_diagnostics = {provider: {"failed_attempts": 0} for provider in HEALTH_TRACKED_PROVIDERS}
    insert_nested_value(config, UNKEYED_PROVIDER_DIAGNOSTICS, provider_diagnostics)
    return config
