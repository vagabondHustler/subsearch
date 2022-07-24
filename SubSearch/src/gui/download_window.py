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


class Create(tk.Frame):
    def __init__(self, parent) -> None:
        tk.Frame.__init__(self, parent)
        self.configure(bg=Tks.bg)

    # create a basic label
    def label(
        self,
        bg=Tks.bg,
        fg=Tks.fg,
        text=None,
        textvar=None,
        row=None,
        col=None,
        anchor=None,
        sticky=None,
        font=Tks.font8b,
        padx=2,
        pady=2,
    ) -> str:
        _label = tk.Label(self, text=text, textvariable=textvar, font=font, fg=fg, anchor=anchor)
        _label.configure(bg=bg, fg=fg, font=font)
        _label.grid(row=row, column=col, sticky=sticky, padx=padx, pady=pady)
        return _label

# replace the regular windows-style title bar with a custom one
