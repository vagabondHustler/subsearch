import json
from pathlib import Path
from typing import Any, Union

from subsearch.data import SUPPORTED_FILE_EXTENSIONS, SUPPORTED_PROVIDERS, app_paths
from subsearch.data.data_objects import AppConfig, LanguageData, ProviderAlphaCodeData
from subsearch.utils import file_manager
from subsearch.utils.exceptions import ProviderNotImplemented

APPCON_JSON = Path(app_paths.appdata_local) / "application_config.json"
LANGS_JSON = Path(app_paths.data) / "languages.json"


def get_json_data(json_file: Path = APPCON_JSON) -> Any:
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


def set_config_key_value(key: str, value: Union[str, int, bool]) -> None:
    """
    Set the value of a key in the config.json file to a specified value.

    Args:
        key (str): A string that represents the key name to modify.
        value (Union[str, int, bool]): A value of String/Integer/Boolean to assign to the specified key.

    Returns:
        None
    """

    with open(APPCON_JSON, "r+", encoding="utf-8") as f:
        data = json.load(f)
        data[key] = value
        f.seek(0)
        json.dump(data, f, indent=4)
        f.truncate()


def set_json_data(data: dict[str, Union[str, int, bool]], json_file: Path = APPCON_JSON) -> None:
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
        "rename_best_match": True,
        "context_menu": True,
        "context_menu_icon": True,
        "manual_download_fail": True,
        "manual_download_mode": False,
        "use_threading": True,
        "multiple_app_instances": False,
        "show_terminal": False,
        "log_to_file": False,
        "file_extensions": dict.fromkeys(SUPPORTED_FILE_EXTENSIONS, True),
        "providers": dict.fromkeys(SUPPORTED_PROVIDERS, True),
    }
    return data


def create_config_file() -> None:
    """
    Creates application_config.json file and set the default values if it doesn't exist and.

    Returns:
        None.
    """
    if APPCON_JSON.exists():
        return None
    application_config = retrieve_application_config()
    with open(APPCON_JSON, "w", encoding="utf-8") as file:
        file.seek(0)
        json.dump(application_config, file, indent=4)
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
        language = get_json_key("current_language")

    data = get_json_data(LANGS_JSON)
    language_data = LanguageData(**data[language])
    return language_data


def get_language_data_value(key: str):
    data = get_language_data()
    return data.__dict__[key]


def get_available_languages() -> dict:
    return get_json_data(LANGS_JSON)


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
        language = get_json_key("current_language")
    data = get_language_data(language)
    if not data.incompatibility:
        return True

    elif provider in data.incompatibility:
        return False
    return False
