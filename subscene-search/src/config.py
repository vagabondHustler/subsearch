import json
from src.os import root_directory_file
from src.data import read_data


def get(output):
    config_json = read_data(root_directory_file("config.json"))

    def language() -> str:
        language = config_json.language
        lang, lang_abbr = language.split(", ")
        return lang, lang_abbr

    def languages() -> list:
        languages = config_json.languages            
        return languages

    if output == "language":
        return language()
    if output == "languages":
        return languages()
