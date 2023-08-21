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
    value = functools.reduce(dict.get, keys, toml_data)  # type: ignore
    return value


def dump_toml_data(toml_file_path: Path, toml_data: dict) -> None:
    with open(toml_file_path, "w") as f:
        toml.dump(toml_data, f)


def update_toml_key(toml_file_path: Path, key: str, value: Any | None) -> None:
    toml_data = load_toml_data(toml_file_path)
    keys = key.split(".")
    functools.reduce(dict.get, keys[:-1], toml_data)[keys[-1]] = value  # type: ignore
    dump_toml_data(toml_file_path, toml_data)


def del_toml_key(toml_file_path: Path, key: str) -> None:
    toml_data = load_toml_data(toml_file_path)
    keys = key.split(".")
    functools.reduce(dict.get, keys[:-1], toml_data).pop(keys[-1], None)  # type: ignore
    dump_toml_data(toml_file_path, toml_data)


def repair_toml_config(toml_file_path: Path, valid_config_keys: list[str], config_keys: list[str]) -> None:
    obsolete_keys = [key for key in config_keys if key not in valid_config_keys]
    for key in obsolete_keys:
        del_toml_key(toml_file_path, key)

    missing_keys = [key for key in valid_config_keys if key not in config_keys]
    for key in missing_keys:
        keys = key.split(".")
        value = functools.reduce(dict.get, keys, DEFAULT_CONFIG)  # type: ignore
        update_toml_key(FILE_PATHS.config, key, value)


def get_keys_recursively(dictionary: dict, prefix="", keys=None) -> list[str]:
    if keys is None:
        keys = []

    if isinstance(dictionary, dict):
        for key in dictionary:
            full_key = f"{prefix}.{key}" if prefix else key
            keys.append(full_key)
            get_keys_recursively(dictionary[key], full_key, keys)

    return keys


def valid_config(valid_config_keys: list[str], config_keys: list[str]) -> bool:
    if not FILE_PATHS.config.exists():
        return False
    valid_config_keys.sort()
    config_keys.sort()
    return config_keys == valid_config_keys


def resolve_on_integrity_failure() -> None:
    if not FILE_PATHS.config.exists():
        dump_toml_data(FILE_PATHS.config, DEFAULT_CONFIG)
        return None
    valid_config_keys = get_keys_recursively(DEFAULT_CONFIG)
    config_keys = get_keys_recursively(load_toml_data(FILE_PATHS.config))
    valid = valid_config(valid_config_keys, config_keys)
    if valid:
        return None
    try:
        repair_toml_config(FILE_PATHS.config, valid_config_keys, config_keys)
    except Exception:
        FILE_PATHS.config.unlink()
        dump_toml_data(FILE_PATHS.config, DEFAULT_CONFIG)


def get_app_config(toml_file_path: Path) -> AppConfig:
    data = load_toml_data(toml_file_path)
    user_data = AppConfig(
        **data["subtitle_filters"],
        **data["gui"],
        subtitle_post_processing=data["subtitle_post_processing"],
        file_extensions=data["file_extensions"],
        providers=data["providers"],
        **data["misc"],
    )
    return user_data
