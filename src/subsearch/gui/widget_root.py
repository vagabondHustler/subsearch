import tkinter as tk

from utils import local_paths

from . import tkinter_data as tkd
from . import tools


def main():
    global root
    root = tk.Tk(className=f" SubSearch")
    root.configure(background=tkd.Color.black)
    icon_path = local_paths.get_path("icons", "16.ico")
    root.iconbitmap(icon_path)
    root.geometry(tools.WindowPosition.set(root))
    root.resizable(False, False)
    tools.CustomBorder(root).place(relx=0.5, rely=0.5, anchor="center")
    tk.Frame(root, height=40, bg=tkd.Color.dark_grey).pack(anchor="center", expand=True)
    tools.CustomTitleBar(root).place(x=tkd.Window.width - 2, y=2, bordermode="inside", anchor="ne")

    return root
