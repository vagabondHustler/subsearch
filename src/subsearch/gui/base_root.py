import tkinter as tk

from subsearch.data import __icon__
from subsearch.data.metadata_classes import TkColor
from subsearch.gui import tk_tools
from subsearch.utils import raw_config, raw_registry


def main():
    if raw_registry.registry_key_exists() is False:
        raw_config.set_default_json()
        raw_registry.add_context_menu()
    root = tk.Tk(className=f"subsearch")
    root.configure(background=TkColor().black)
    root.iconbitmap(__icon__)
    root.geometry(tk_tools.WindowPosition.set(root))
    root.resizable(False, False)
    return root
