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
        subsearch_config (Path): The default subsearch_config.toml file location
        languages_config (Path): The default languages_config.toml file location
    """

    subsearch_log: Path
    subsearch_config: Path
    language_data: Path


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
    """
    Represents the configuration settings for an application.

    This class is a data structure used to store various configuration settings for an application.
    These settings include preferences related to language, subtitle types, file extensions, providers,
    automatic actions, context menu options, system tray, logging, and other features.

    Attributes:
        current_language (str): The current language setting for the application.
        subtitle_type (dict[str, bool]): A dictionary representing subtitle types and their enabled status.
        foreign_only (bool): Show only foreign subtitles while searching.
        percentage_threshold (int): The threshold subtitles has to pass to be downloaded.
        autoload_rename (bool): Automatically rename downloaded subtitles.
        autoload_move (bool): Automatically move downloaded subtitles to the appropriate folder.
        autoload_dir (bool): Target directory of 'autoload_move.
        context_menu (bool): Show context menu options.
        context_menu_icon (bool): Display icons in the context menu.
        system_tray (bool): Support a system tray.
        toast_summary (bool): Display toast notifications.
        manual_download_on_fail (bool): Application open the gui `download_manager` screen.
        show_terminal (bool): Show the terminal/console.
        use_threading (bool): Use threading.
        multiple_app_instances (bool): Application allows multiple instances.
        log_to_file (bool): Log output to a file.
        file_extensions (dict[str, bool]): A dictionary representing file extensions and their enabled status.
        providers (dict[str, bool]): A dictionary representing subtitle providers and their enabled status.
        hearing_impaired (bool): Show hearing-impaired subtitles.
        non_hearing_impaired (bool): Show non-hearing-impaired subtitles.

    Examples:
        Creating an `AppConfig` instance:

        >>> config = AppConfig(
        ...     current_language="english",
        ...     subtitle_type={"hearing_impaired": True, "non_hearing_impaired": False},
        ...     foreign_only=False,
        ...     percentage_threshold=90,
        ...     autoload_rename=True,
        ...     autoload_move=True,
        ...     autoload_dir="."
        ...     context_menu=True,
        ...     context_menu_icon=True,
        ...     system_tray=True,
        ...     toast_summary=True,
        ...     manual_download_on_fail=True,
        ...     show_terminal=False,
        ...     use_threading=True,
        ...     multiple_app_instances=False,
        ...     log_to_file=True,
        ...     file_extensions={"mkv": True, "avi": False ...},
        ...     providers={"subscene_site": True, "opensubtitles_site": True, "opensubtitles_hash": True ...},
        ...     hearing_impaired=False,
        ...     non_hearing_impaired=True,
        ... )
    """

    current_language: str
    subtitle_type: dict[str, bool]
    foreign_only: bool
    percentage_threshold: int
    autoload_rename: bool
    autoload_move: bool
    autoload_dir: str
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
    """
    Represents Subscene website preferences stored in a cookie.

    Store various preferences of a user's Subscene preferences.
    The cookie preferences include settings for dark theme, sorting subtitles by date,
    language filter, hearing impaired filter, and foreign subtitles only.

    Attributes:
        dark_theme (bool): True if the user has enabled dark theme, False otherwise.
        sort_subtitle_by_date (str): The preferred sorting option for subtitles by date.
        language_filter (int): The language filter setting for subtitles.
        hearing_impaired (int): The hearing impaired filter setting for subtitles.
        foreign_only (bool): True if the user prefers foreign subtitles only, False otherwise.

    Examples:
        Creating a `SubsceneCookie` instance:

        >>> cookie = SubsceneCookie(dark_theme=True, sort_subtitle_by_date=false,
        ...                         language_filter=1, hearing_impaired=0, foreign_only=False)
    """

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
    """
    Represents system information.

    This class is a data structure used to hold information about the system,
    including the platform, mode, Python version, and subsearch.

    Attributes:
        platform (str): The platform or operating system of the system.
        mode (str): The mode or state of the system.
        python (str): The version of Python installed on the system.
        subsearch (str): The subsearch associated with the system.

    Examples:
        Creating a `SystemInfo` instance:

        >>> system_info = SystemInfo(platform="windows-10-10.0.22624-sp0", mode="interpreter", python="3.11.4", subsearch="2.37.1")
    """

    platform: str
    mode: str
    python: str
    subsearch: str
