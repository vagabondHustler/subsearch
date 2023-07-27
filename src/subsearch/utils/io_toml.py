import functools
from pathlib import Path
from typing import Any, Union

import toml

from subsearch.data.constants import DEFAULT_CONFIG, FILE_PATHS
from subsearch.data.data_classes import AppConfig


def load_toml_data(toml_file_path: Path) -> dict[str, Any]:
    with open(toml_file_path, "r") as f:
        return toml.load(f)


def load_toml_value(toml_file_path: Path, key: str) -> Any:
    toml_data = load_toml_data(toml_file_path)
    keys = key.split(".")
    value = functools.reduce(dict.get, keys, toml_data) # type: ignore
    return value


def dump_toml_data(toml_file_path: Path, toml_data: dict) -> None:
    with open(toml_file_path, "w") as f:
        toml.dump(toml_data, f)


def update_toml_key(toml_file_path: Path, key: str, value: Union[str, int, bool]) -> None:
    toml_data = load_toml_data(toml_file_path)
    keys = key.split(".")
    functools.reduce(dict.get, keys[:-1], toml_data)[keys[-1]] = value # type: ignore
    dump_toml_data(toml_file_path, toml_data)


def del_toml_key(toml_file_path: Path, key: str) -> None:
    toml_data = load_toml_data(toml_file_path)
    keys = key.split(".")
    functools.reduce(dict.get, keys[:-1], toml_data).pop(keys[-1], None) # type: ignore
    dump_toml_data(toml_file_path, toml_data)


def add_toml_key(toml_file_path: Path, key: str, value: Union[str, int, bool]) -> None:
    toml_data = load_toml_data(toml_file_path)
    keys = key.split(".")
    functools.reduce(dict.get, keys[:-1], toml_data)[keys[-1]] = value # type: ignore
    dump_toml_data(toml_file_path, toml_data)


def repair_toml_config(toml_file_path: Path) -> None:
    """
    Updates the application's configuration file to match the desired config,
    preserving existing values.

    Returns:
        None.
    """
    default_config = DEFAULT_CONFIG
    toml_data = load_toml_data(toml_file_path)

    obsolete_keys = [key for key in toml_data if key not in default_config]
    for key in obsolete_keys:
        del_toml_key(toml_file_path, key)

    missing_keys = [key for key in default_config if key not in toml_data]
    for key in missing_keys:
        toml_data[key] = default_config[key]

    dump_toml_data(FILE_PATHS.subsearch_config, toml_data)


def get_keys_recursively(dictionary: dict) -> list[str]:
    keys: list[str] = []
    if isinstance(dictionary, dict):
        for key in dictionary:
            keys.append(key)
            keys.extend(get_keys_recursively(dictionary[key]))
    return keys


def validate_app_config_integrity() -> bool:
    """
    Checks the integrity of the application's configuration file.

    Returns:
        bool: True if the configuration is intact, False otherwise.
    """
    if not FILE_PATHS.subsearch_config.exists():
        return False
    default_config = get_keys_recursively(DEFAULT_CONFIG)
    subsearch_config = get_keys_recursively(load_toml_data(FILE_PATHS.subsearch_config))
    default_config.sort()
    subsearch_config.sort()
    return subsearch_config == default_config


def resolve_on_integrity_failure() -> None:
    """
    Resolves the application's configuration if the integrity check fails.
    Re-creates the configuration file with default values if the repair operation fails.

    Returns:
        None.
    """
    if not validate_app_config_integrity() and FILE_PATHS.subsearch_config.exists():
        try:
            repair_toml_config(FILE_PATHS.subsearch_config)
        except Exception:
            FILE_PATHS.subsearch_config.unlink()
            dump_toml_data(FILE_PATHS.subsearch_config, DEFAULT_CONFIG)


def get_app_config(toml_file_path: Path) -> AppConfig:
    """
    Returns an instance of AppConfig that contains the current configuration settings.

    Returns:
        AppConfig: instance containing the current application configuration settings.
    """
    data = load_toml_data(toml_file_path)
    user_data = AppConfig(
        **data["subtitle_filters"],
        **data["gui"],
        autoload=data["autoload"],
        file_extensions=data["file_extensions"],
        providers=data["providers"],
        **data["misc"],
    )
    return user_data
