from dataclasses import dataclass
from pathlib import Path


@dataclass(order=True)
class SubsearchPaths:
    """
    Dataclass containing paths to modules and assets
    """

    home: str
    data: str
    gui: str
    providers: str
    utils: str
    icon: str
    titlebar: str
    tabs: str


@dataclass(order=True)
class VideoFileData:
    """
    Dataclass containing the video file base information
    """

    name: str
    ext: str
    path: Path
    directory: Path
    subs_directory: Path
    tmp_directory: Path


@dataclass(order=True)
class UserData:
    """
    Dataclass containing the users different app configurations
    """

    current_language: str
    languages: dict[str, str]
    subtitle_type: dict[str, bool]
    percentage: int
    rename_best_match: bool
    context_menu_icon: bool
    show_download_window: bool
    show_terminal: bool
    log_to_file: bool
    file_ext: dict[str, bool]
    providers: dict[str, bool]
    language_code3: str
    hearing_impaired: bool
    non_hearing_impaired: bool


@dataclass(frozen=True, order=True)
class ReleaseData:
    """
    Dataclass containing parsed data from a video file
    """

    title: str
    year: int
    season: str
    season_ordinal: str
    episode: str
    episode_ordinal: str
    series: bool
    release: str
    group: str
    file_hash: str


@dataclass(frozen=True, order=True)
class ProviderUrlData:
    """
    Dataclass containing urls for providers
    """

    subscene: str
    opensubtitles: str
    opensubtitles_hash: str
    yifysubtitles: str


@dataclass(frozen=True, order=True)
class DownloadData:
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
class FormattedData:
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
class TkWindowSize:
    """
    Dataclass containing different window sizes for the GUI
    """

    width: int = 738
    height: int = 720


@dataclass(frozen=True, order=True)
class TkColor:
    """
    Dataclass containing different colors for the GUI
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
class TkFont:
    """
    Dataclass containing different fonts and their styles and or size
    """

    cas6b: str = "Cascadia 6 bold"
    cas8: str = "Cascadia 8"
    cas8i: str = "Cascadia 8 italic"
    cas8b: str = "Cascadia 8 bold"
    cas10b: str = "Cascadia 10 bold"
    cas11: str = "Cascadia 11"
    cas20b: str = "Cascadia 20 bold"
