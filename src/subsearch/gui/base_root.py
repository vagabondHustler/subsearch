import tkinter as tk

from subsearch.data import GUI_DATA, __paths__
from subsearch.gui import tk_tools
from subsearch.utils import raw_config, raw_registry


def main():
    if raw_registry.registry_key_exists() is False:
        raw_config.set_default_json()
        raw_registry.add_context_menu()
    root = tk.Tk(className=f"subsearch")
    root.configure(background=GUI_DATA.colors.black)
    root.iconbitmap(__paths__.icon)
    root.geometry(tk_tools.WindowPosition.set(root))
    root.resizable(False, False)
    return root
