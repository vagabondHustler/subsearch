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
class CustomTitleBar(tk.Frame):
    def __init__(self, parent) -> None:
        tk.Frame.__init__(self, parent)
        self.after(10, self.remove_titlebar, root)
        self.parent = parent
        self._offsetx = 0
        self._offsety = 0
        root.focus_force()
        root.overrideredirect(True)
        button = Create.button(
            self,
            text="X",
            row=0,
            col=0,
            height=1,
            width=2,
            abgc="#cd2e3e",
            bge="#a72633",
            fge=Tks.fg,
            font=Tks.font10b,
            pady=5,
            padx=5,
            bind_to=self.tk_exit_press,
        )
        label = tk.Label(
            root,
            text=" SubSearch",
            height=2,
            bg=Tks.bc,
            fg=Tks.fg,
            font=Tks.font10b,
            justify="left",
            anchor="w",
            width=Tks.window_width,
        )
        label.place(bordermode="outside", x=0, y=0)
        label.lower()
        self.button = button
        self.label = label

        label.bind("<Button-1>", self.titlebar_press)
        label.bind("<B1-Motion>", self.titlebar_drag)

        self.configure(bg=Tks.bc)

    def window_pos(self, parent, w: int = 80, h: int = 48) -> str:
        ws = parent.winfo_screenwidth()
        hs = parent.winfo_screenheight()

        x = int((ws / 2) - (w / 2))
        y = int((hs / 2) - (h / 2))
        value = f"{w}x{h}+{x}+{y}"
        return value

    def remove_titlebar(self, parent) -> None:
        GWL_EXSTYLE = -20
        WS_EX_APPWINDOW = 0x00040000
        WS_EX_TOOLWINDOW = 0x00000080
        hwnd = ctypes.windll.user32.GetParent(root.winfo_id())
        style = ctypes.windll.user32.GetWindowLongPtrW(hwnd, GWL_EXSTYLE)
        style = style & ~WS_EX_TOOLWINDOW
        style = style | WS_EX_APPWINDOW
        res = ctypes.windll.user32.SetWindowLongPtrW(hwnd, GWL_EXSTYLE, style)
        root.withdraw()
        root.after(10, root.deiconify)

    def titlebar_press(self, event) -> None:
        self._offsetx = root.winfo_pointerx() - root.winfo_rootx()
        self._offsety = root.winfo_pointery() - root.winfo_rooty()

    def titlebar_drag(self, event) -> None:
        x = self.winfo_pointerx() - self._offsetx
        y = self.winfo_pointery() - self._offsety
        root.geometry(f"+{x}+{y}")

    def tk_exit_release(self, event) -> None:
        clean_up(cwd(), "temp.txt")
        root.destroy()

    def tk_exit_press(self, event) -> None:
        self.button.bind("<ButtonRelease-1>", self.tk_exit_release)


