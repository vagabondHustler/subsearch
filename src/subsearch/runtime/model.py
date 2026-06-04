from dataclasses import Field, dataclass
from enum import Enum
from pathlib import Path
from typing import Any, ClassVar, Protocol


@dataclass(order=True)
class LanguageData:
    name: str
    two_letter_code: str
    three_letter_code: str
    incompatibility: list[str]


@dataclass(order=True, slots=True)
class ProviderLetterCodeData:
    provider: str
    letter_code: str


@dataclass(order=True, slots=True)
class AppPaths:
    home: Path
    data: Path
    ui_assets: Path
    providers: Path
    io: Path
    parsing: Path
    tmp_dir: Path
    appdata_subsearch: Path


@dataclass(order=True, slots=True)
class FilePaths:
    log: Path
    config: Path
    subtitle_languages: Path


@dataclass(order=True, slots=True)
class VideoFile:
    file_exist: bool
    filename: str
    file_hash: str
    file_extension: str
    file_path: Path
    file_directory: Path
    subs_dir: Path
    tmp_dir: Path


@dataclass(order=True, slots=True)
class AppConfig:
    selected_language: str
    accept_threshold: int
    hearing_impaired: bool
    non_hearing_impaired: bool
    only_foreign_parts: bool
    providers: dict[str, bool]
    context_menu: bool
    context_menu_icon: bool
    file_extensions: dict[str, bool]
    system_tray: bool
    summary_notification: bool
    automatic_downloads: bool
    always_open_manager: bool
    open_manager_on_no_matches: bool
    post_processing: dict[str, Any]
    show_terminal: bool
    single_instance: bool
    api_call_limit: int
    request_connect_timeout: int
    request_read_timeout: int
    diagnostics: dict[str, Any]


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
    precentage_result: int
    provider_name: str
    subtitle_name: str
    download_url: str
    request_data: dict[str, Any]


class ProviderHealth(Enum):
    OK = "ok"
    NO_RESPONSE = "no_response"
    STRUCTURE_INVALID = "structure_invalid"


@dataclass(order=True, slots=True)
class ProviderResult:
    provider_name: str
    health: ProviderHealth
    subtitles_found: int


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
    long_paths: str


class GenericDataClass(Protocol):
    __dataclass_fields__: ClassVar[dict[str, Field[Any]]]


@dataclass(order=True, slots=True)
class ProviderApiLimit:
    opensubtitles: int
    yifysubtitles: int
    subsource: int
