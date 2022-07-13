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

class SelectLanguage(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        svar = tk.StringVar()
        svar.set(f"{language}, {lang_abbr}")
        number_of_buttons = len(TLANGUAGE)
        self.svar = svar
        _xstr = " " * 50
        _rowcountert = 0
        _colcountert = 1
        for i in range(1, 4):
            self.create_label(t=_xstr, r=0, c=i, f=TFONT10)
        self.create_label(t="Selected language", r=1, c=1, f=TFONT10)
        self.create_label(r=1, c=2, f=TFONT10)
        for i in range(number_of_buttons):
            _rowcountert += 1
            if _rowcountert == 8:
                _colcountert += 1
                _rowcountert = 1
            self.create_button(r=_rowcountert + 1, c=_colcountert, x=i)
        self.configure(bg=TBG)

    def set_language(self, event):
        btn = event.widget
        self.svar.set(btn.cget("text"))
        update_svar = self.svar.get()
        update_json("language", update_svar)

    def create_label(self, t=None, r=1, c=1, p="nsew", f=TFONT10):
        if t is None:
            label = tk.Label(self, textvariable=self.svar, anchor="center")
        else:
            label = tk.Label(self, text=t, anchor="w")
        label.configure(bg=TBG, fg=TFG, font=f)
        label.grid(row=r, column=c, sticky=p, padx=2, pady=2)

    def create_button(self, r=0, c=0, x=None):
        button = tk.Button(self, text=TLANGUAGE[x], height=1, width=24, bd=0)
        button.configure(bg=TBC, fg=TFG, font=TFONT10)
        button.grid(row=r, column=c, padx=2, pady=2)
        button.bind("<Button-1>", self.set_language)
