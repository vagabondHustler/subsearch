import json
from pathlib import Path
from typing import Any, Union

from subsearch.data.constants import FILE_PATHS, SUPPORTED_FILE_EXT, SUPPORTED_PROVIDERS
from subsearch.data.data_classes import AppConfig, LanguageData, ProviderAlphaCodeData
from subsearch.utils.exceptions import ProviderNotImplemented


def get_json_data(json_file: Path) -> Any:
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


def get_json_key(key: str, json_file: Path) -> Any:
    """
    Get values of keys in config.json

    Args:
        key (str):
        current_language, languages, subtitle_type, percentage_threshold,
        rename_best_match, context_menu, context_menu_icon, manual_download_on_fail, use_threading,
        show_terminal, log_to_file, file_extensions, providers

    Returns:
        Any: value
    """
    return get_json_data(json_file)[f"{key}"]


def set_config_key_value(key: str, value: Union[str, int, bool], json_file: Path) -> None:
    """
    Set the value of a key in the config.json file to a specified value.

    Args:
        key (str): A string that represents the key name to modify.
        value (Union[str, int, bool]): A value of String/Integer/Boolean to assign to the specified key.

    Returns:
        None
    """

    with open(json_file, "r+", encoding="utf-8") as f:
        data = json.load(f)
        data[key] = value
        f.seek(0)
        json.dump(data, f, indent=4)
        f.truncate()


def set_json_data(data: dict[str, Union[str, int, bool]], json_file: Path) -> None:
    """
    Writes the provided configuration data to the config.json file.

    Args:
        data: A dictionary containing configuration data with keys as strings and values as an instance
                of either a string, int or boolean type.

    Returns:
        None
    """
    with open(json_file, "w") as f:
        f.seek(0)
        json.dump(data, f, indent=4)
        f.truncate()


def retrieve_application_config() -> dict[str, Any]:
    subtitle_types = ["hearing_impaired", "non_hearing_impaired"]
    data = {
        "current_language": "english",
        "subtitle_type": dict.fromkeys(subtitle_types, True),
        "foreign_only": False,
        "percentage_threshold": 90,
        "autoload_rename": True,
        "autoload_move": True,
        "context_menu": True,
        "context_menu_icon": True,
        "system_tray": True,
        "toast_summary": False,
        "manual_download_on_fail": True,
        "use_threading": True,
        "multiple_app_instances": False,
        "show_terminal": False,
        "log_to_file": False,
        "file_extensions": dict.fromkeys(SUPPORTED_FILE_EXT, True),
        "providers": dict.fromkeys(SUPPORTED_PROVIDERS, True),
    }
    return data


def create_config_file() -> None:
    """
    Creates application_config.json file and set the default values if it doesn't exist and.

    Returns:
        None.
    """
    if FILE_PATHS.subsearch_config.exists():
        return None
    application_config = retrieve_application_config()
    with open(FILE_PATHS.subsearch_config, "w", encoding="utf-8") as file:
        file.seek(0)
        json.dump(application_config, file, indent=4)
        file.truncate()


def get_app_config(json_file: Path) -> AppConfig:
    """
    Returns an instance of AppConfig that contains the current configuration settings.

    Returns:
        AppConfig: instance containing the current application configuration settings.
    """
    data = get_json_data(json_file)
    user_data = AppConfig(
        **data,
        hearing_impaired=data["subtitle_type"]["hearing_impaired"],
        non_hearing_impaired=data["subtitle_type"]["non_hearing_impaired"],
    )
    return user_data


def get_language_data(language: str = "default") -> LanguageData:
    """
    Get the language data object for the provided language from the languages.json configuration file.

    Args:
        language: The language for which to retrieve the data. Defaults to the current language stored in the application
                configuration if not specified.

    Returns:
        A LanguageData object containing the data associated with the specified language.
    """
    if language == "default":
        language = get_json_key("current_language", FILE_PATHS.subsearch_config)

    data = get_json_data(FILE_PATHS.languages_config)
    language_data = LanguageData(**data[language])
    return language_data


def get_language_data_value(key: str):
    data = get_language_data()
    return data.__dict__[key]


def get_available_languages() -> dict:
    return get_json_data(FILE_PATHS.languages_config)


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


def check_language_compatibility(provider: str, language: str = "default") -> bool:
    if language == "default":
        language = get_json_key("current_language", FILE_PATHS.subsearch_config)
    data = get_language_data(language)
    if not data.incompatibility:
        return True

    elif provider in data.incompatibility:
        return False
    return False


def update_config_file() -> None:
    """
    Updates the application's configuration file to match the desired config,
    preserving existing values.

    Returns:
        None.
    """
    if not FILE_PATHS.subsearch_config.exists():
        return

    config_dict = retrieve_application_config()
    json_data = get_json_data()

    keys_to_remove = []
    for key in json_data:
        if key not in config_dict:
            keys_to_remove.append(key)

    for key in keys_to_remove:
        json_data.pop(key)

    keys_to_add = []
    for key in config_dict:
        if key not in json_data:
            keys_to_add.append(key)

    for key in keys_to_add:
        json_data[key] = config_dict[key]

    set_json_data(json_data)


def extract_dict_keys(dictionary, keys=[]) -> list:
    """
    Extracts all keys from a nested dictionary.

    Args:
        dictionary (dict): The dictionary to extract keys from.
        keys (list, optional): The list of parent keys. Defaults to [].

    Returns:
        list: List of keys in the dictionary.
    """
    if keys is None:
        keys = []
    json_keys = []
    for key, value in dictionary.items():
        nested_keys = keys + [key]
        if isinstance(value, dict):
            json_keys.extend(extract_dict_keys(value, nested_keys))
        else:
            json_keys.append(".".join(nested_keys))
    return json_keys
