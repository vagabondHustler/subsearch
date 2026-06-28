from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class Language:
    name: str
    two_letter_code: str
    three_letter_code: str
    incompatibility: list[str]
    tvsubtitles_code: str = ""


@dataclass(slots=True)
class AppConfig:
    selected_language: str
    accept_threshold: int
    hearing_impaired: bool
    non_hearing_impaired: bool
    only_foreign_parts: bool
    providers: dict[str, bool]
    downloads_per_provider: int
    token_weights: dict[str, float]
    token_multipliers: dict[str, float]
    context_menu: bool
    context_menu_icon: bool
    file_extensions: dict[str, bool]
    system_tray: bool

    notification_display_duration: float
    notification_play_sound: bool
    search_mode: str
    subtitle_workspace_manual_post_processing: bool
    post_processing: dict[str, Any]
    paths: dict[str, Any]
    mica_effect: bool
    show_terminal: bool
    show_tray_icon: bool
    single_instance: bool
    request_connect_timeout: int
    request_read_timeout: int
    diagnostics: dict[str, Any]
    subsource_api_key_exists: bool
    subsource_api_key: str
