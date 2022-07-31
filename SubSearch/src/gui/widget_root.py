import tkinter as tk

from src.gui import tools, tkinter_data as tkd
from src.utilities import local_paths


def main():
    global root
    root = tk.Tk(className=f" SubSearch")
    icon_path = local_paths.root_directory("data", "16.ico")
    root.iconbitmap(icon_path)
    root.geometry(tools.WindowPosition.set(root))
    root.resizable(False, False)
    root.wm_attributes("-transparentcolor", tkd.Color.grey)
    root.configure(bg=tkd.Color.dark_grey)
    cb = tools.CustomBorder(root)
    cb.place(relx=0.5, rely=0.5, anchor="center")
    ctb = tools.CustomTitleBar(root)
    ctb.place(x=tkd.Window.width - 2, y=2, bordermode="inside", anchor="ne")
    tk.Frame(root, bg=tkd.Color.dark_grey).pack(anchor="center", expand=True)
    tk.Frame(root, bg=tkd.Color.dark_grey).pack(anchor="center", expand=True)
    tk.Frame(root, bg=tkd.Color.dark_grey).pack(anchor="center", expand=True)
    ctb.lift()
    cb.lift()

    return root
