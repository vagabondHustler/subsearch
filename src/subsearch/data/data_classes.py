from dataclasses import dataclass
from pathlib import Path


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
    """
    A dataclass representing the paths used in the application.

    Attributes:
        home (Path): The root directory of the application.
        data (Path): The directory where data related to the application is stored.
        gui (Path): The directory containing GUI modules and files.
        providers (Path): The directory containing subtitle provider modules.
        utils (Path): The directory containing utility modules.
        tmp_dir(Path): The directory containing temporary files & folders.
        appdata_subsearch(Path): The directory containing the persistent application files.
    """

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
    """
    A dataclass representing the files used in the application.

    Attributes:
        subsearch_log (Path): The default subsearch_log.log file location
        subsearch_config (Path): The default subsearch_config.json file location
        languages_config (Path): The default languages_config.json file location
    """

    subsearch_log: Path
    subsearch_config: Path
    languages_config: Path


@dataclass(order=True, slots=True)
class VideoFile:
    """
     Class representing file information.

    Attributes:
        filename (str): Name of the file.
        file_extension (str): Extension of the file.
        file_path (pathlib.Path): Path of the file.
        directory (pathlib.Path): Directory path of the file.
        subs_directory (pathlib.Path): Subtitles directory path.
        tmp_directory (pathlib.Path): Temporary directory path.
    """

    filename: str
    file_hash: str
    file_extension: str
    file_path: Path
    file_directory: Path
    subs_dir: Path
    tmp_dir: Path


@dataclass(order=True, slots=True)
class AppConfig:
    current_language: str
    subtitle_type: dict[str, bool]
    foreign_only: bool
    percentage_threshold: int
    autoload_rename: bool
    autoload_move: bool
    context_menu: bool
    context_menu_icon: bool
    system_tray: bool
    toast_summary: bool
    manual_download_on_fail: bool
    show_terminal: bool
    use_threading: bool
    multiple_app_instances: bool
    log_to_file: bool
    file_extensions: dict[str, bool]
    providers: dict[str, bool]
    hearing_impaired: bool
    non_hearing_impaired: bool


@dataclass(order=True, slots=True)
class SubsceneCookie:
    dark_theme: bool
    sort_subtitle_by_date: str
    language_filter: int
    hearing_impaired: int
    foreigen_only: bool


@dataclass(order=True, slots=True)
class ReleaseData:
    """
    Data class representing data associated with a media release.

    Attributes:
        title (str): Title of the media.
        year (int): Year of the media release.
        season (str): Season of the media.
        season_ordinal (str): Ordinal of the season.
        episode (str): Episode of the media.
        episode_ordinal (str): Ordinal of the episode.
        tvseries (bool): Boolean flag indicating if the media is a TV series.
        release (str): Name of the media release.
        group (str): Name of the release group.
    """

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
    """
    A dataclass to represent URLs for different subtitle providers.

    Attributes:
        subscene(str): URL of the subscene provider.
        opensubtitles(str): URL of the opensubtitles provider.
        opensubtitles_hash(str): Hash URL of the opensubtitles provider.
        yifysubtitles(str): URL of the yifysubtitles provider.
    """

    subscene: str
    opensubtitles: str
    opensubtitles_hash: str
    yifysubtitles: str


@dataclass(order=True, slots=True)
class Subtitle:
    """
    A data class representing download data for subtitle.

    Attributes:
        pct_result (str): How closely the release_name matches the release name of the video file.
        provider (str): The subtitle provider used to obtain the subtitle file.
        file_path (str): The path to the subtitle file on the local filesystem.
        download_url (str): The URL from which the subtitle file can be downloaded from.
    """

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
