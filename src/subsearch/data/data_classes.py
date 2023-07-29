from dataclasses import dataclass
from pathlib import Path
from typing import Union


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
        language_data (Path): The default language_data.toml file location
    """

    log: Path
    config: Path
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
    This class is a data structure used to store various configuration options for an application.
    These options include preferences related to subtitle filters, file extensions, providers,
    automatic actions, context menu options, logging, and other features.

    Attributes:
        language (str): The language setting for the application.
        accept_threshold (int): The threshold value for accepting subtitles.
        hearing_impaired (bool): A flag indicating whether to include hearing-impaired subtitles.
        non_hearing_impaired (bool): A flag indicating whether to include non-hearing-impaired subtitles.
        only_foreign_parts (bool): A flag indicating whether to include only foreign parts subtitles.
        context_menu (bool): A flag indicating whether to enable context menu options.
        context_menu_icon (bool): A flag indicating whether to display icons in the context menu.
        system_tray (bool): A flag indicating whether to enable the application in the system tray.
        summary_notification (bool): A flag indicating whether to display summary notifications.
        show_terminal (bool): A flag indicating whether to show the terminal in the application.
        autoload (dict[str, Union[bool, str]]): A dictionary containing autoload options.
        file_extensions (dict[str, bool]): A dictionary containing file extensions.
        providers (dict[str, bool]): A dictionary containing provider options.
        manual_download_on_fail (bool): A flag indicating whether to enable manual downloads on failure.
        multithreading (bool): A flag indicating whether to enable multithreading.
        single_instance (bool): A flag indicating whether to enable single-instance mode.
        logging (bool): A flag indicating whether to enable logging for the application.

    Examples:
        >>> config = AppConfig(
        ...     language="english",
        ...     accept_threshold=False,
        ...     hearing_impaired=90,
        ...     non_hearing_impaired=True,
        ...     only_foreign_parts=True,
        ...     context_menu=True,
        ...     context_menu_icon=True,
        ...     system_tray=True,
        ...     summary_notification=True,
        ...     show_terminal=False,
        ...     autoload={"rename": True, "move": True, "target_path": "."},
        ...     file_extensions=False,
        ...     providers=True,
        ...     manual_download_on_fail={"mkv": True, "avi": False ...},
        ...     multithreading={"subscene_site": True, "opensubtitles_site": True, "opensubtitles_hash": True ...},
        ...     single_instance=False,
        ...     logging=True,
        ... )
    """

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
    subtitle_post_processing: dict[str, Union[bool, str]]
    file_extensions: dict[str, bool]
    providers: dict[str, bool]
    manual_download_on_fail: bool
    multithreading: bool
    single_instance: bool
    logging: bool


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
