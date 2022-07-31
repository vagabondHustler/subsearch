import tkinter as tk

from src.gui.functions import CustomBorder, CustomTitleBar, WindowPosition
from src.gui.data import Window, Color
from src.utilities.local_paths import root_directory
from src.utilities.version import current_version


CURRENT_VERSION = current_version()


def main():
    global root
    root = tk.Tk(className=f" SubSearch")
    icon_path = root_directory("data", "16.ico")
    root.iconbitmap(icon_path)
    root.geometry(WindowPosition.set(root))
    root.resizable(False, False)
    root.wm_attributes("-transparentcolor", Color.grey)
    root.configure(bg=Color.dark_grey)
    cb = CustomBorder(root)
    cb.place(relx=0.5, rely=0.5, anchor="center")
    ctb = CustomTitleBar(root)
    ctb.place(x=Window.width - 2, y=2, bordermode="inside", anchor="ne")
    tk.Frame(root, bg=Color.dark_grey).pack(anchor="center", expand=True)
    tk.Frame(root, bg=Color.dark_grey).pack(anchor="center", expand=True)
    tk.Frame(root, bg=Color.dark_grey).pack(anchor="center", expand=True)
    ctb.lift()
    cb.lift()

    return root
