import tkinter as tk

from subsearch.data import __icons__
from subsearch.gui import tk_data, tk_tools
from subsearch.utils import current_user, raw_config, raw_registry

TKWINDOW = tk_data.Window()
TKCOLOR = tk_data.Color()


def main():
    if current_user.got_key() is False:
        raw_config.set_default_json()
        raw_registry.add_context_menu()
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
