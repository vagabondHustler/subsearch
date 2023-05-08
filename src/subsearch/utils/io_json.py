import json
from pathlib import Path
from typing import Any, Union

from subsearch.data import app_paths
from subsearch.data.data_objects import AppConfig, LanguageData, ProviderAlphaCodeData
from subsearch.utils.exceptions import ProviderNotImplemented

APPLICATION_CONFIG_JSON = Path(app_paths.data) / "application_config.json"
LANGUAGES_JSON = Path(app_paths.data) / "languages.json"


def get_json_data(json_file: Path = APPLICATION_CONFIG_JSON) -> Any:
    """
    Returns the contents of the json file as a Python object.

    Args:
        None

    Returns:
        Any: The contents of config.json file.
    """
    with open(json_file, encoding="utf-8") as file:
        data = json.load(file)
    return data


def get_json_key(key: str) -> Any:
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
    return get_json_data()[f"{key}"]


_current_language: str = get_json_key("current_language")

#
#       subsearch/data/application_config.json
#


def set_config_key_value(key: str, value: Union[str, int, bool]) -> None:
    """
    Set the value of a key in the config.json file to a specified value.

    Args:
        key (str): A string that represents the key name to modify.
        value (Union[str, int, bool]): A value of String/Integer/Boolean to assign to the specified key.

    Returns:
        None
    """

    with open(APPLICATION_CONFIG_JSON, "r+", encoding="utf-8") as f:
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
    with open(APPLICATION_CONFIG_JSON, "w") as f:
        f.seek(0)
        json.dump(data, f, indent=4)
        f.truncate()


def set_default_json() -> None:
    """
    Sets default values to keys that are present inside config.json file and modifies the same file.

    Returns:
        None.
    """

    data = get_json_data()
    data["current_language"] = "english"
    data["subtitle_type"] = dict.fromkeys(data["subtitle_type"], True)
    data["percentage_threshold"] = 90
    data["rename_best_match"] = True
    data["context_menu"] = True
    data["context_menu_icon"] = True
    data["manual_download_fail"] = True
    data["manual_download_mode"] = False
    data["use_threading"] = True
    data["multiple_app_instances"] = False
    data["show_terminal"] = False
    data["log_to_file"] = False
    data["file_extensions"] = dict.fromkeys(data["file_extensions"], True)
    data["providers"] = dict.fromkeys(data["providers"], True)
    with open(APPLICATION_CONFIG_JSON, "r+", encoding="utf-8") as file:
        file.seek(0)
        json.dump(data, file, indent=4)
        file.truncate()


def get_app_config() -> AppConfig:
    """
    Returns an instance of AppConfig that contains the current configuration settings.

    Returns:
        AppConfig: instance containing the current application configuration settings.
    """
    data = get_json_data()
    user_data = AppConfig(
        **data,
        hearing_impaired=data["subtitle_type"]["hearing_impaired"],
        non_hearing_impaired=data["subtitle_type"]["non_hearing_impaired"],
    )
    return user_data


def get_language_data(language: str = _current_language) -> LanguageData:
    """
    Get the language data object for the provided language from the languages.json configuration file.

    Args:
        language: The language for which to retrieve the data. Defaults to the current language stored in the application
                configuration if not specified.

    Returns:
        A LanguageData object containing the data associated with the specified language.
    """

    data = get_json_data(LANGUAGES_JSON)
    language_data = LanguageData(**data[language])
    return language_data


def get_available_languages() -> dict:
    return get_json_data(LANGUAGES_JSON)


def get_provider_alpha_code_type(provider: str) -> ProviderAlphaCodeData:
    """
    Generates ProviderAlphaCodeType object containing provider and its associated alpha code.

    Args:
        provider (str): a string specifying the name of the provider

    Returns:
        ProviderAlphaCodeType: an instance of ProviderAlphaCodeType with the given provider and its associated alpha code_
    """
    providers = {"subscene": "name", "opensubtitles": "alpha_2b", "yifisubtitles": "name"}
    if provider not in providers:
        raise ProviderNotImplemented
    return ProviderAlphaCodeData(provider, providers[provider])


def get_alpha_code(alpha_code_type: str) -> str:
    language_data = get_language_data()
    return getattr(language_data, alpha_code_type)


def get_provider_alpha_code(provider: str) -> str:
    data = get_provider_alpha_code_type(provider)
    return get_alpha_code(data.alpha_code)


def check_language_compatibility(provider: str, language: str = _current_language) -> bool:
    data = get_language_data(language)
    if not data.incompatibility:
        return True

    elif provider in data.incompatibility:
        return False
    return False
