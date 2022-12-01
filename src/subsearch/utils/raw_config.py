import json
from pathlib import Path
from typing import Any, Union

from subsearch.data import __data__
from subsearch.data.metadata_classes import ApplicationSettings


def set_config_key_value(key: str, value: Union[str, int, bool]) -> None:
    config_file = Path(__data__) / "config.json"
    with open(config_file, "r+", encoding="utf-8") as f:
        data = json.load(f)
        data[key] = value
        f.seek(0)
        json.dump(data, f, indent=4)
        f.truncate()


def set_config(data):
    config_file = Path(__data__) / "config.json"
    with open(config_file, "w") as f:
        f.seek(0)
        json.dump(data, f, indent=4)
        f.truncate()


def get_config() -> Any:
    config_file = Path(__data__) / "config.json"
    with open(config_file, encoding="utf-8") as file:
        data = json.load(file)

    return data


def get_config_key(key: str) -> Any:
    """
    Get values of keys in config.json

    Args:
        key (str):

        - User settings

        "hearing_impaired: bool | str", "percentage: int"

        - GUI stuff

        "cm_icon: bool", "manual_download_tab: bool",
        "show_terminal: bool", "file_ext: dict"

    Returns:
        Any: value
    """
    config_json_dict = {
        "current_language": get_config()["current_language"],
        "languages": get_config()["languages"],
        "subtitle_type": get_config()["subtitle_type"],
        "percentage_threshold": get_config()["percentage_threshold"],
        "rename_best_match": get_config()["rename_best_match"],
        "context_menu_icon": get_config()["context_menu_icon"],
        "manual_download_tab": get_config()["manual_download_tab"],
        "use_threading": get_config()["use_threading"],
        "show_terminal": get_config()["show_terminal"],
        "log_to_file": get_config()["log_to_file"],
        "file_extensions": get_config()["file_extensions"],
        "providers": get_config()["providers"],
    }
    return config_json_dict[f"{key}"]


def set_default_json() -> None:
    # set default config.json values
    data = get_config()
    data["current_language"] = "English"
    data["subtitle_type"] = dict.fromkeys(data["subtitle_type"], True)
    data["percentage_threshold"] = 90
    data["rename_best_match"] = True
    data["context_menu_icon"] = True
    data["manual_download_tab"] = True
    data["use_threading"] = False
    data["show_terminal"] = False
    data["log_to_file"] = False
    data["file_extensions"] = dict.fromkeys(data["file_extensions"], True)
    data["providers"] = dict.fromkeys(data["providers"], True)
    config_file = Path(__data__) / "config.json"
    with open(config_file, "r+", encoding="utf-8") as file:
        file.seek(0)
        json.dump(data, file, indent=4)
        file.truncate()


def get_user_data() -> ApplicationSettings:
    config_file = Path(__data__) / "config.json"
    with open(config_file, encoding="utf-8") as file:
        data = json.load(file)
    user_data = ApplicationSettings(
        **data,
        language_iso_639_3=data["languages"][data["current_language"]],
        hearing_impaired=data["subtitle_type"]["hearing_impaired"],
        non_hearing_impaired=data["subtitle_type"]["non_hearing_impaired"],
    )
    return user_data
