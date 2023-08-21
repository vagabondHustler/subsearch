from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(order=True)
class LanguageData:
    name: str
    alpha_1: str
    alpha_2b: str
    incompatibility: list[str]
    subscene_id: int


@dataclass(order=True, slots=True)
class ProviderAlphaCodeData:
    provider: str
    alpha_code: str


@dataclass(order=True, slots=True)
class AppPaths:
    home: Path
    data: Path
    gui: Path
    gui_assets: Path
    gui_styles: Path
    providers: Path
    utils: Path
    tmp_dir: Path
    appdata_subsearch: Path


@dataclass(order=True, slots=True)
class FilePaths:
    log: Path
    config: Path
    language_data: Path


@dataclass(order=True, slots=True)
class VideoFile:
    filename: str
    file_hash: str
    file_extension: str
    file_path: Path
    file_directory: Path
    subs_dir: Path
    tmp_dir: Path


@dataclass(order=True, slots=True)
class AppConfig:
    language: str
    accept_threshold: int
    hearing_impaired: bool
    non_hearing_impaired: bool
    only_foreign_parts: bool
    context_menu: bool
    context_menu_icon: bool
    system_tray: bool
    summary_notification: bool
    show_terminal: bool
    subtitle_post_processing: dict[str, Any]
    file_extensions: dict[str, bool]
    providers: dict[str, bool]
    manual_download_on_fail: bool
    multithreading: bool
    single_instance: bool


@dataclass(order=True, slots=True)
class SubsceneCookie:
    dark_theme: bool
    sort_subtitle_by_date: str
    language_filter: int
    hearing_impaired: int
    foreigen_only: bool


@dataclass(order=True, slots=True)
class ReleaseData:
    title: str
    year: int
    season: str
    season_ordinal: str
    episode: str
    episode_ordinal: str
    tvseries: bool
    release: str
    group: str


@dataclass(order=True, slots=True)
class ProviderUrls:
    subscene: str
    opensubtitles: str
    opensubtitles_hash: str
    yifysubtitles: str


@dataclass(order=True, slots=True)
class Subtitle:
    pct_result: int
    provider: str
    release_name: str
    download_url: str


@dataclass(order=True, frozen=True)
class SystemInfo:
    platform: str
    mode: str
    python: str
    subsearch: str


@dataclass(order=True, slots=True, frozen=True)
class WindowsRegistryPaths:
    classes: str
    asterisk: str
    shell: str
    subsearch: str
    subsearch_command: str
