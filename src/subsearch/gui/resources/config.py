from dataclasses import dataclass


@dataclass(order=True, frozen=True)
class Size:
    """
    Sub dataclass containing sizes for the GUI
    """

    width: int = 800
    height: int = 680


@dataclass(order=True, frozen=True)
class Position:
    """
    Sub dataclass containing sizes for the GUI
    """

    screen_x: int = int(Size().width / 2)
    screen_y: int = int(Size().height / 2 - 41)
    screen_hidden_x: int = int(Size().width * 2)


@dataclass(order=True, frozen=True)
class Color:
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
        default_fg: #bdbdbd
        default_bg: #1a1b1b
        default_bg_dark: #111111
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
    default_fg: str = "#bdbdbd"
    default_bg: str = "#1a1b1b"
    default_bg_dark: str = "#111111"
    light_black: str = "#0e0e0e"
    black: str = "#151515"
    dark_black: str = "#000000"


@dataclass(order=True, frozen=True)
class Font:
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


size = Size()
position = Position()
font = Font()
color = Color()


DEFAULT_LABEL_CONFIG = dict(bg=color.default_bg, fg=color.default_fg, font=font.cas8b)
DEFAULT_LABEL_GRID = dict(row=0, column=0, sticky="w", padx=2, pady=2)
DEFAULT_BTN_TOGGLE_GRID = dict(row=0, column=2, pady=2)
