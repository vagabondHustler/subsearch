import ctypes
import sys
import tkinter as tk
from dataclasses import dataclass

from src.gui.tooltip import Hovertip
from src.scraper.subscene_soup import get_download_url
from src.utilities.file_manager import (clean_up, download_zip_auto,
                                        extract_zips)
from src.utilities.local_paths import cwd, root_directory
from src.utilities.version import current_version


@dataclass
class Tks:
    """
    Dataclass with often used values for the graphical user interface
    """

    window_width: int = 760
    window_height: int = 760
    bg: str = "#1b1d22"
    bgl: str = "#4c4c4c"
    fg: str = "#bdbdbd"
    fge: str = "#c5895e"
    bc: str = "#121417"
    abg: str = "#16181c"
    abg_disabled: str = "#303030"
    font8: str = "Cascadia 8"
    font8b: str = "Cascadia 8 bold"
    font10b: str = "Cascadia 8 bold"
    font10b: str = "Cascadia 10 bold"
    font20b: str = "Cascadia 20 bold"
    col58: str = " " * 58


