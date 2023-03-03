import json
from pathlib import Path
from typing import Any, Union

from subsearch.data import __paths__
from subsearch.data.data_objects import AppConfig


def set_config_key_value(key: str, value: Union[str, int, bool]) -> None:
    """
    Set the value of a key in the config.json file to a specified value.

    Args:
        key (str): A string that represents the key name to modify.
        value (Union[str, int, bool]): A value of String/Integer/Boolean to assign to the specified key.

    Returns:
        None
    """
    config_file = Path(__paths__.data) / "config.json"

    with open(config_file, "r+", encoding="utf-8") as f:
        data = json.load(f)
        data[key] = value
        f.seek(0)
        json.dump(data, f, indent=4)
        f.truncate()


def set_config(data: dict[str, Union[str, int, bool]]) -> None:
    """
    Writes the provided configuration data to the config.json file.

    Args:
        data: A dictionary containing configuration data with keys as strings and values as an instance
                 of either a string, int or boolean type.

    Returns:
        None
    """
    config_file = Path(__paths__.data) / "config.json"
    with open(config_file, "w") as f:
        f.seek(0)
        json.dump(data, f, indent=4)
        f.truncate()


def get_config() -> Any:
    """
    Returns the contents of the config.json file as a Python object.

    Args:
        None

    Returns:
        Any: The contents of config.json file.
    """
    config_file = Path(__paths__.data) / "config.json"
    with open(config_file, encoding="utf-8") as file:
        data = json.load(file)
    return data


def get_config_key(key: str) -> Any:
    """
    Get values of keys in config.json

    Args:
        key (str):
        current_language, languages, subtitle_type, percentage_threshold,
        rename_best_match, context_menu, context_menu_icon, manual_download_fail, use_threading,
        show_terminal, log_to_file, file_extensions, providers

    Returns:
        Any: value
    """
    return get_config()[f"{key}"]


def set_default_json() -> None:
    """
    Sets default values to keys that are present inside config.json file and modifies the same file.

    Returns:
        None.
    """

    # set default config.json values
    data = get_config()
    data["current_language"] = "English"
    data["subtitle_type"] = dict.fromkeys(data["subtitle_type"], True)
    data["percentage_threshold"] = 90
    data["rename_best_match"] = True
    data["context_menu"] = True
    data["context_menu_icon"] = True
    data["manual_download_fail"] = True
    data["manual_download_mode"] = False
    data["use_threading"] = True
    data["show_terminal"] = False
    data["log_to_file"] = False
    data["file_extensions"] = dict.fromkeys(data["file_extensions"], True)
    data["providers"] = dict.fromkeys(data["providers"], True)
    config_file = Path(__paths__.data) / "config.json"
    with open(config_file, "r+", encoding="utf-8") as file:
        file.seek(0)
        json.dump(data, file, indent=4)
        file.truncate()


def get_app_config() -> AppConfig:
    """
    Returns an instance of AppConfig that contains the current configuration settings.

    Returns:
        AppConfig: instance containing the current application configuration settings.
    """
    config_file = Path(__paths__.data) / "config.json"
    with open(config_file, encoding="utf-8") as file:
        data = json.load(file)
    user_data = AppConfig(
        **data,
        language_iso_639_3=data["languages"][data["current_language"]],
        hearing_impaired=data["subtitle_type"]["hearing_impaired"],
        non_hearing_impaired=data["subtitle_type"]["non_hearing_impaired"],
    )
    return user_data
