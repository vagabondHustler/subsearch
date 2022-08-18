import tkinter as tk
from typing import Any

from gui import tkdata as tkd

from subsearch.data import __icons__
from subsearch.gui import tools

TKCOLOR = tkd.Color()
TKWINDOW = tkd.Window()


def main():
    global root
    root = tk.Tk(className=f" SubSearch")
    root.configure(background=TKCOLOR.black)
    icon_path = f"{__icons__}\\16.ico"
    root.iconbitmap(icon_path)
    root.geometry(tools.WindowPosition.set(root))
    root.resizable(False, False)
    tools.CustomBorder(root).place(relx=0.5, rely=0.5, anchor="center")
    tk.Frame(root, height=40, bg=TKCOLOR.dark_grey).pack(anchor="center", expand=True)
    tools.CustomTitleBar(root).place(x=TKWINDOW.width - 2, y=2, bordermode="inside", anchor="ne")

    return root
