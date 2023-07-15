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
        tmpdir(Path): The directory containing temporary files & folders.
        appdata_local(Path): The directory containing the persistent application files.
    """

    home: Path
    data: Path
    gui: Path
    gui_assets: Path
    gui_styles: Path
    providers: Path
    utils: Path
    tmpdir: Path
    appdata_local: Path


@dataclass(order=True, slots=True)
class FileData:
    """
     Class representing file information.

    Attributes:
        filename (str): Name of the file.
        file_extension (str): Extension of the file.
        file_path (pathlib.Path): Path of the file.
        directory_path (pathlib.Path): Directory path of the file.
        subs_directory (pathlib.Path): Subtitles directory path.
        tmp_directory (pathlib.Path): Temporary directory path.
    """

    filename: str
    file_extension: str
    file_path: Path
    directory_path: Path
    subs_directory: Path
    tmp_directory: Path


@dataclass(order=True, slots=True)
class AppConfig:
    """
    Data class for storing user preferences and settings.

    Attributes:
        current_language (str): The currently selected language.
        subtitle_type (dict[str, bool]): A dictionary used to store user's preference regarding subtitle types.
        percentage_threshold (int): Percentage threshold value for preferred match results.
        rename_best_match (bool): Boolean flag to rename the closest matching srt file with the media file used in search.
        context_menu (bool): Boolean flag representing whether or not to display SubSearch in the context menu on Windows platform.
        context_menu_icon (bool): Boolean flag representing whether or not to display the SubSearch icon in the context menu on Windows platform.
        manual_download_fail (bool): Boolean flag indicating if the GUI download screen should be opened.
        manual_download_mode (bool): Boolean flag to toggle manual download mode.
        show_terminal (bool): Boolean flag indicating if terminal output is displayed.
        use_threading (bool): Boolean flag indicating if threads are enabled when downloading subtitles.
        log_to_file (bool): Boolean flag that indicates if logging is enabled.
        file_extensions (dict[str, bool]): A dictionary storing user's preferences regarding file extensions.
        providers (dict[str, bool]): A dictionary storing user's preferences regarding subtitle providers.
        hearing_impaired (bool): Boolean flag indicating if the subtitle is for hearing-impaired people.
        non_hearing_impaired (bool): Boolean flag indicating if the subtitle is not for hearing-impaired people.
    """

    current_language: str
    subtitle_type: dict[str, bool]
    foreign_only: bool
    percentage_threshold: int
    rename_best_match: bool
    context_menu: bool
    context_menu_icon: bool
    system_tray: bool
    toast_summary: bool
    manual_download_fail: bool
    manual_download_mode: bool
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


@dataclass(order=True, frozen=True, slots=True)
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
        file_hash (str): Hash value of the media file.
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
    file_hash: str


@dataclass(order=True, frozen=True, slots=True)
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


@dataclass(order=True, frozen=True, slots=True)
class DownloadData:
    """
    A data class representing metadata for the to be downloaded subtitle file.

    Attributes:
        provider (str): The subtitle provider used to obtain the subtitle file.
        name (str): The name of the media file associated with the subtitle file.
        file_path (str): The path to the subtitle file on the local filesystem.
        url (str): The URL from which the subtitle file can be downloaded from.
        idx_num (int): Index in which order the file is downloaded.
        idx_length (int): The total length of index.
    """

    provider: str
    name: str
    file_path: str
    url: str
    idx_num: int
    idx_lenght: int


@dataclass(order=True, frozen=True, slots=True)
class PrettifiedDownloadData:
    """
    Represents prettified version of DownloadData.

    Attributes:
        provider (str): The name of the metadata provider.
        release (str): The name of the movie or TV show release.
        url (str): The URL from which the subtitle file can be downloaded from.
        pct_result (int): The percentage match between the search query and
            the metadata.
        formatted_release (str): The formatted name of the release.
        formatted_url (str): The formatted URL of the metadata.
    """

    provider: str
    release: str
    url: str
    pct_result: int
    formatted_release: str
    formatted_url: str

SUPPORTED_FILE_EXTENSIONS = [
    ".avi",
    ".mp4",
    ".mkv",
    ".mpg",
    ".mpeg",
    ".mov",
    ".rm",
    ".vob",
    ".wmv",
    ".flv",
    ".3gp",
    ".3g2",
    ".swf",
    ".mswmm",
]
SUPPORTED_PROVIDERS = ["opensubtitles_site", "opensubtitles_hash", "subscene_site", "yifysubtitles_site"]
