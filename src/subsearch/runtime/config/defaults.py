from typing import Any

from subsearch.io.nested_dict import insert_nested_value
from subsearch.runtime.keys import ConfigKey

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

SUPPORTED_PROVIDERS: list[str] = ["opensubtitles", "yifysubtitles_site", "subsource_site"]

HEALTH_TRACKED_PROVIDERS: list[str] = ["imdb", "opensubtitles", "yifysubtitles", "subsource"]

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
        ConfigKey.NOTIFICATIONS_SUMMARY_NOTIFICATION: False,
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
