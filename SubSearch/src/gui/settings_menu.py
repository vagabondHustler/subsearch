import os
import sys
import tkinter as tk
import webbrowser

import src.utilities.edit_registry as edit_registry
from src.data._version import current_version
from src.utilities.current_user import got_key, is_admin, run_as_admin
from src.utilities.edit_config import set_default_values, update_json
from src.utilities.fetch_config import get
from src.utilities.updates import check_for_updates

if is_admin():
    if got_key() is False:
        set_default_values()
        edit_registry.add_context_menu()
elif got_key:
    run_as_admin()
    exit()

WINDOW_WIDTH = 560
WINDOW_HEIGHT = 530
TBG = "#1b1d22"
TSLBG = "#4c4c4c"
TFG = "#bdbdbd"
TBC = "#121417"
TEC = "#494B52"
TFONT10 = "Cascadia 8 bold"
TFONT20 = "Cascadia 20 bold"
TLANGUAGE = (
    "Arabic, ar",
    "Brazillian Portuguese, pt_BR",
    "Danish, dk",
    "Dutch, nl",
    "English, en",
    "Finnish, fi",
    "French, fr",
    "German, de",
    "Hebrew, he",
    "Indonesian, id",
    "Italian, it",
    "Korean, ko",
    "Norwegian, no",
    "Romanian, ro",
    "Spanish, es",
    "Swedish, sv",
    "Thai, th",
    "Turkish, tr",
    "Vietnamese, vi",
)


language, lang_abbr = get("language")
precentage = get("percentage")
terminal_focus = get("terminal_focus")
hearing_impared = get("hearing_impaired")
cm_icon = get("cm_icon")

def set_window_position(w=WINDOW_WIDTH, h=WINDOW_HEIGHT):
    # get screen width and height
    ws = root.winfo_screenwidth()  # width of the screen
    hs = root.winfo_screenheight()  # height of the screen

    # calculate x and y coordinates for the Tk root window
    x = int((ws / 2) - (w / 2))
    y = int((hs / 2) - (h / 2))
    value = f"{w}x{h}+{x}+{y}"
    return value

class MenuTitle(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.create_label("Menu", 1, 1, "nsew", TFONT20)
        self.configure(bg=TBG)

    def create_label(self, t=None, r=1, c=1, p="nsew", f=TFONT20):

        label = tk.Label(self, text=t, anchor="w")
        label.configure(bg=TBG, fg=TFG, font=f)
        label.grid(row=r, column=c, sticky=p, padx=2, pady=2)
