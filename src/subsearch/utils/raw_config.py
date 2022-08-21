import json
from typing import Any, Union

from subsearch.data import __data__


# update config.json
def set_config_json(key: str, value: Union[str, int, bool]) -> None:
    """
    Set values of keys in config.json

    Args:
        key (str):
        value (str | int | bool): store language:str (lang, abbr... eg English, en)
    """
    config_file = f"{__data__}\\config.json"
    with open(config_file, "r+", encoding="utf-8") as f:
        data = json.load(f)
        data[key] = value
        f.seek(0)
        json.dump(data, f, indent=4)
        f.truncate()


def get_json() -> Any:
    config_file = f"{__data__}\\config.json"
    with open(config_file, encoding="utf-8") as file:
        data = json.load(file)

    return data


# get said value(s) from config.json
def get_config_key(key: str) -> Any:
    """
    Get values of keys in config.json

    Args:
        key (str):

        - User settings

        "language: tuple", "languages: list", "other_languages: list",
        "hearing_impaired: bool | str", "percentage: int"

        - GUI stuff

        "cm_icon: bool", "show_download_window: bool",
        "show_terminal: bool", "file_ext: dict"

    Returns:
        Any: value
    """
    config_json_dict = {
        "language": get_json()["language"].split(", "),
        "languages": get_json()["languages"],
        "other_languages": get_json()["other_languages"],
        "hearing_impaired": get_json()["hearing_impaired"],
        "percentage": get_json()["percentage_pass"],
        "cm_icon": get_json()["context_menu_icon"],
        "show_download_window": get_json()["show_download_window"],
        "show_terminal": get_json()["show_terminal"],
        "file_ext": get_json()["file_ext"],
    }
    return config_json_dict[f"{key}"]


# set default config.json values
def set_default_json() -> None:
    data = get_json()
    data["language"] = "English, en"
    data["hearing_impaired"] = "Both"
    data["percentage_pass"] = 90
    data["context_menu_icon"] = True
    data["show_download_window"] = True
    data["show_terminal"] = False
    data["file_ext"] = dict.fromkeys(data["file_ext"], True)
    config_file = f"{__data__}\\config.json"
    with open(config_file, "r+", encoding="utf-8") as file:
        file.seek(0)
        json.dump(data, file, indent=4)
        file.truncate()
