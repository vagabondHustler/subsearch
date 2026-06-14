from typing import Any

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


def get_default_app_config() -> dict[str, Any]:
    file_extensions = dict.fromkeys(SUPPORTED_FILE_EXTENSIONS, True)
    providers = dict.fromkeys(SUPPORTED_PROVIDERS, True)
    provider_diagnostics = {provider: {"failed_attempts": 0} for provider in HEALTH_TRACKED_PROVIDERS}
    return {
        "language": {
            "selected": "english",
        },
        "search": {
            "accept_threshold": 90,
            "hearing_impaired": True,
            "non_hearing_impaired": True,
            "only_foreign_parts": False,
            "providers": providers,
            "downloads_per_provider": 4,
            "token_weights": {**DEFAULT_TOKEN_WEIGHTS},
            "token_multipliers": {**DEFAULT_TOKEN_MULTIPLIERS},
        },
        "shell_integration": {
            "context_menu": True,
            "context_menu_icon": True,
            "file_extensions": file_extensions,
        },
        "notifications": {
            "system_tray": True,
            "summary_notification": False,
        },
        "download_manager": {
            "search_mode": "hybrid",
            "manually_handle_post_processing": False,
        },
        "post_processing": {
            "rename": True,
            "move_best": True,
            "move_all": False,
        },
        "paths": {
            "download_directory": "",
            "extraction_directory": "",
            "video_file_directory": ".",
            "path_resolution": "relative",
            "create_missing_directory": True,
        },
        "application": {
            "show_terminal": False,
            "single_instance": True,
        },
        "network": {
            "request_connect_timeout": 4,
            "request_read_timeout": 5,
        },
        "diagnostics": {
            "enabled": True,
            "failed_attempts_threshold": 3,
            "provider_diagnostics": provider_diagnostics,
        },
        "credentials": {
            "subsource": {
                "api_key_exists": False,
                "api_key": "",
            },
        },
    }
