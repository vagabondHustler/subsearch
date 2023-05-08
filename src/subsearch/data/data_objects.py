from dataclasses import dataclass
from pathlib import Path


@dataclass(order=True)
class LanguageData:
    name: str
    alpha_1: str
    alpha_2b: str
    incompatibility: list[str]


@dataclass(order=True)
class ProviderAlphaCodeData:
    provider: str
    alpha_code: str


@dataclass(order=True)
class AppPaths:
    """
    A dataclass representing the paths used in the application.

    Attributes:
        home (Path): The root directory of the application.
        data (Path): The directory where data related to the application is stored.
        gui (Path): The directory containing GUI modules and files.
        providers (Path): The directory containing subtitle provider modules.
        utils (Path): The directory containing utility modules.
        icon (Path): The Path object representing the icon for the application.
        tabs (Path): The directory containing tab icon assets for the GUI.
    """

    home: Path
    data: Path
    gui: Path
    providers: Path
    utils: Path
    icon: Path
    tabs: Path


@dataclass(order=True)
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


@dataclass(order=True)
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
        manual_download_fail (bool): Boolean flag indicating if the GUI download tab should be opened.
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
    percentage_threshold: int
    rename_best_match: bool
    context_menu: bool
    context_menu_icon: bool
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


@dataclass(frozen=True, order=True)
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


@dataclass(frozen=True, order=True)
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


@dataclass(frozen=True, order=True)
class DownloadMetaData:
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


@dataclass(frozen=True, order=True)
class FormattedMetadata:
    """
    Represents formatted metadata for a movie or TV show release.

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


@dataclass(frozen=True, order=True)
class GUISizes:
    """
    Sub dataclass containing sizes for the GUI
    """

    root_width: int = 738
    root_height: int = 720


@dataclass(frozen=True, order=True)
class GUIPositions:
    """
    Sub dataclass containing sizes for the GUI
    """

    content_x: int = int(GUISizes().root_width / 2)
    content_y: int = int(GUISizes().root_height / 2 - 41)
    content_hidden_x: int = int(GUISizes().root_width * 2)


@dataclass(frozen=True, order=True)
class GUIColors:
    """
    Sub dataclass containing colors for the GUI

    Colors:
        purple: #b294bb
        red: #bc473b
        dark_red: #89332a
        red_brown: #b26947,
        orange: #ab7149
        light_orange: #de935f
        yellow: #f0c674
        blue: #81a2be
        cyan: #82b3ac
        green: #9fa65d
        green_brown: #a59256
        grey: #4c4c4c
        light_grey: #727272
        silver_grey: #8a8a8a
        white_grey: #bdbdbd
        dark_grey: #1a1b1b
        mid_grey_black: #111111
        light_black: #0e0e0e
        black: #151515
        dark_black: #000000
    """

    purple: str = "#b294bb"
    red: str = "#bc473b"
    dark_red: str = "#89332a"
    black_red: str = "#4b1713"
    red_brown: str = "#b26947"
    orange: str = "#ab7149"
    light_orange: str = "#de935f"
    yellow: str = "#f0c674"
    blue: str = "#81a2be"
    cyan: str = "#82b3ac"
    green: str = "#9fa65d"
    green_brown: str = "#a59256"
    grey: str = "#4c4c4c"
    light_grey: str = "#727272"
    silver_grey: str = "#8a8a8a"
    white_grey: str = "#bdbdbd"
    dark_grey: str = "#1a1b1b"
    mid_grey_black: str = "#111111"
    light_black: str = "#0e0e0e"
    black: str = "#151515"
    dark_black: str = "#000000"


@dataclass(frozen=True, order=True)
class GUIFonts:
    """
    Sub dataclass containing fonts and their styles and or size

    Fonts:
        cas6b: Cascadia 6 bold
        cas8: Cascadia 8
        cas8i: Cascadia 8 italic
        cas8b: Cascadia 8 bold
        cas10b: Cascadia 10 bold
        cas11: Cascadia 11
        cas20b: Cascadia 20 bold
    """

    cas6b: str = "Cascadia 6 bold"
    cas8: str = "Cascadia 8"
    cas8i: str = "Cascadia 8 italic"
    cas8b: str = "Cascadia 8 bold"
    cas10b: str = "Cascadia 10 bold"
    cas11: str = "Cascadia 11"
    cas20b: str = "Cascadia 20 bold"


@dataclass(frozen=True, order=True)
class GUIData:
    """
    Dataclass containing GUI data
    """

    size = GUISizes
    pos = GUIPositions
    fonts = GUIFonts
    colors = GUIColors


GUI_DATA = GUIData()
