from dataclasses import Field, dataclass
from pathlib import Path
from typing import Any, ClassVar, Protocol

from subsearch.providers import yifysubtitles


@dataclass(order=True)
class LanguageData:
    name: str
    alpha_1: str
    alpha_2b: str
    incompatibility: list[str]


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
    open_on_no_matches: bool
    always_open: bool
    no_automatic_downloads: bool
    single_instance: bool


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
    imdb_id: str


@dataclass(order=True, slots=True)
class ProviderUrls:
    opensubtitles: str
    opensubtitles_hash: str
    yifysubtitles: str
    subsource: str


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


class GenericDataClass(Protocol):
    __dataclass_fields__: ClassVar[dict[str, Field[Any]]]


@dataclass(order=True, slots=True)
class ProviderApiLimit:
    opensubtitles: int
    yifysubtitles: int
    subsource: int


@dataclass(order=True, slots=True)
class SubtitleUndetermined:
    provider: str
    precentage_result: int
    passed_threshold: bool
    data: dict[str, Any]
