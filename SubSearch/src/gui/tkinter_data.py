from dataclasses import dataclass


@dataclass
class Window:
    """
    Class for storing settings for window size.

    Args:
    width: width of window in pixels.
    height: height of window in pixels.
    """

    width: int = 700
    height: int = 700


@dataclass
class Color:
    """
    Class for storing colors for widgets.

    Args:
    purple: "#b294bb"
    red: "#bc473b"
    dark_red: "#89332a"
    red_brown: "#b26947"
    orange: "#ab7149"
    light_orange: "#de935f"
    yellow: "#f0c674"
    blue: "#81a2be"
    cyan: "#82b3ac"
    green: "#9fa65d"
    green_brown: "#a59256"
    grey: "#4c4c4c"
    light_grey: "#727272"
    dark_grey: "#1A1A1A"
    silver_grey: "#8a8a8a"
    white_grey: "#bdbdbd"
    light_black: "#0e0e0e"
    black: "#151515"
    dark_black: "#000000"
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
    dark_grey: str = "#1A1A1A"
    silver_grey: str = "#8a8a8a"
    white_grey: str = "#bdbdbd"
    light_black: str = "#0e0e0e"
    black: str = "#151515"
    dark_black: str = "#000000"


@dataclass
class Font:
    """
    Class for storing fonts for widgets

    Args:
    cas6b: "Cascadia 6 bold"
    cas8: "Cascadia 8"
    cas8i: "Cascadia 8 italic"
    cas8b: "Cascadia 8 bold"
    cas10b: "Cascadia 10 bold"
    cas11: "Cascadia 11"
    cas20b: "Cascadia 20 bold"
    """

    cas6b: str = "Cascadia 6 bold"
    cas8: str = "Cascadia 8"
    cas8i: str = "Cascadia 8 italic"
    cas8b: str = "Cascadia 8 bold"
    cas10b: str = "Cascadia 10 bold"
    cas11: str = "Cascadia 11"
    cas20b: str = "Cascadia 20 bold"


@dataclass
class Misc:
    """
    Class for storing misc settings.

    Args:
    col58: " " * 58
    """

    col58: str = " " * 58
