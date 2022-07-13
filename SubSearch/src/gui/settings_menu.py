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
