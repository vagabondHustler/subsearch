import tkinter as tk

from subsearch.data import __icons__, __version__
from subsearch.gui import tk_data, tk_tools

TKWINDOW = tk_data.Window()
TKCOLOR = tk_data.Color()


def main():
    global root
    root = tk.Tk(className=f"Subsearch")
    root.configure(background=TKCOLOR.black)
    icon_path = f"{__icons__}\\16.ico"
    root.iconbitmap(icon_path)
    root.geometry(tk_tools.WindowPosition.set(root))
    root.resizable(False, False)
    tk_tools.CustomBorder(root).place(relx=0.5, rely=0.5, anchor="center")
    tk.Frame(root, height=40, bg=TKCOLOR.dark_grey).pack(anchor="center", expand=True)
    tk_tools.CustomTitleBar(root).place(x=TKWINDOW.width - 2, y=2, bordermode="inside", anchor="ne")

    return root
