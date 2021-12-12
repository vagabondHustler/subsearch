import json
from src.sos import root_directory_file
from src.data import read_data


def get(output):
    config_json = read_data(root_directory_file("config.json"))

    def language() -> str:
        language = config_json.language
        lang, lang_abbr = language.split(", ")
        return lang, lang_abbr

    def languages() -> list:
        ls = config_json.languages
        return ls

    def precent() -> int:
        p = config_json.precentage_pass
        return p

    def terminal_focus() -> str:
        tf = config_json.terminal_focus
        return tf

    def terminal_in() -> str:
        ti = config_json.terminal_in
        return ti

    def cm_icon() -> str:
        cm = config_json.context_menu_icon
        return cm

    if output == "language":
        return language()
    if output == "languages":
        return languages()
    if output == "percentage":
        return precent()
    if output == "terminal_focus":
        return terminal_focus()
    if output == "terminal_in":
        return terminal_in()
    if output == "cm_icon":
        return cm_icon()
