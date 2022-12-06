from dataclasses import dataclass
from pathlib import Path


@dataclass(order=True)
class AppPaths:
    """
    Dataclass containing paths to modules and assets
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
    Dataclass containing the video file base information
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
    Dataclass containing the users different app configurations
    """

    current_language: str
    languages: dict[str, str]
    subtitle_type: dict[str, bool]
    percentage_threshold: int
    rename_best_match: bool
    context_menu_icon: bool
    manual_download_tab: bool
    show_terminal: bool
    use_threading: bool
    log_to_file: bool
    file_extensions: dict[str, bool]
    providers: dict[str, bool]
    language_iso_639_3: str
    hearing_impaired: bool
    non_hearing_impaired: bool


@dataclass(frozen=True, order=True)
class ReleaseMetadata:
    """
    Dataclass containing parsed data from a video file
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
    Dataclass containing urls for providers
    """

    subscene: str
    opensubtitles: str
    opensubtitles_hash: str
    yifysubtitles: str


@dataclass(frozen=True, order=True)
class DownloadMetaData:
    """
    Dataclass with all the necessary data for downloading a file
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
    Dataclass containing information that can later be downloaded
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
