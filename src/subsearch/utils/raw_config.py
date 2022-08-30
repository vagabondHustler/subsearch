import json
import os
from typing import Any, NamedTuple, Union

from subsearch.data import __data__


# update config.json
def set_config_key_value(key: str, value: Union[str, int, bool]) -> None:
    config_file = f"{__data__}\\config.json"
    with open(config_file, "r+", encoding="utf-8") as f:
        data = json.load(f)
        data[key] = value
        f.seek(0)
        json.dump(data, f, indent=4)
        f.truncate()


def set_config(data):
    config_file = os.path.join(__data__, "config.json")
    with open(config_file, "w") as f:
        f.seek(0)
        json.dump(data, f, indent=4)
        f.truncate()


def get_config() -> Any:
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

        "hearing_impaired: bool | str", "percentage: int"

        - GUI stuff

        "cm_icon: bool", "show_download_window: bool",
        "show_terminal: bool", "file_ext: dict"

    Returns:
        Any: value
    """
    config_json_dict = {
        "current_language": get_config()["current_language"],
        "languages": get_config()["languages"],
        "hearing_impaired": get_config()["hearing_impaired"],
        "percentage": get_config()["percentage"],
        "context_menu_icon": get_config()["context_menu_icon"],
        "show_download_window": get_config()["show_download_window"],
        "show_terminal": get_config()["show_terminal"],
        "file_ext": get_config()["file_ext"],
        "providers": get_config()["providers"],
    }
    return config_json_dict[f"{key}"]


def set_default_json() -> None:
    # set default config.json values
    data = get_config()
    data["current_language"] = "English"
    data["hearing_impaired"] = "Both"
    data["percentage"] = 90
    data["context_menu_icon"] = True
    data["show_download_window"] = True
    data["show_terminal"] = False
    data["file_ext"] = dict.fromkeys(data["file_ext"], True)
    data["providers"] = dict.fromkeys(data["providers"], True)
    config_file = f"{__data__}\\config.json"
    with open(config_file, "r+", encoding="utf-8") as file:
        file.seek(0)
        json.dump(data, file, indent=4)
        file.truncate()


class UserParameters(NamedTuple):
    current_language: str
    hearing_impaired: bool | str
    pct: int
    show_dl_window: bool
