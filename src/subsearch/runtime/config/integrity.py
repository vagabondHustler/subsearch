import functools
import os
from pathlib import Path
from typing import Any

from subsearch.io import json_file
from subsearch.runtime.config.composition import DEFAULT_CONFIG, FILE_PATHS
from subsearch.runtime.config.nested_dict import (
    delete_nested_value,
    get_keys_recursively,
    set_nested_value,
)
from subsearch.runtime.recorder import LogLevel, capture


class ConfigResolution:
    def __init__(self, config_data: dict[str, Any], is_fresh: bool) -> None:
        self.config_data = config_data
        self.is_fresh = is_fresh


def repair_config(config_file_path: Path, valid_config_keys: list[str], config_keys: list[str]) -> None:
    capture("Config schema mismatch, repairing", level=LogLevel.WARNING)
    config_data = json_file.load_json_data(config_file_path)

    obsolete_keys = [key for key in config_keys if key not in valid_config_keys]
    for key in obsolete_keys:
        capture(f"Removing obsolete config key {key}")
        delete_nested_value(config_data, key)

    missing_keys = [key for key in valid_config_keys if key not in config_keys]
    for key in missing_keys:
        capture(f"Adding missing config key {key}")
        keys = key.split(".")
        value = functools.reduce(dict.get, keys, DEFAULT_CONFIG)  # type: ignore
        set_nested_value(config_data, key, value)

    json_file.dump_json_data(config_file_path, config_data)


def valid_config(valid_config_keys: list[str], config_keys: list[str]) -> bool:
    if not FILE_PATHS.config.exists():
        return False
    valid_config_keys.sort()
    config_keys.sort()
    return config_keys == valid_config_keys


def remove_stale_temp_file() -> None:
    temp_file_path = FILE_PATHS.config.with_suffix(f"{FILE_PATHS.config.suffix}.tmp")
    temp_file_path.unlink(missing_ok=True)


def remove_stale_backup_file() -> None:
    backup_file_path = FILE_PATHS.config.with_suffix(f"{FILE_PATHS.config.suffix}.bak")
    backup_file_path.unlink(missing_ok=True)


def reset_to_default_config() -> None:
    capture("Settings reset to defaults", level=LogLevel.WARNING)
    FILE_PATHS.config.unlink(missing_ok=True)
    json_file.dump_json_data(FILE_PATHS.config, DEFAULT_CONFIG)


def restore_last_known_good_config() -> None:
    backup_file_path = FILE_PATHS.config.with_suffix(f"{FILE_PATHS.config.suffix}.bak")
    if not backup_file_path.exists():
        return None
    capture("Restored settings from backup")
    os.replace(backup_file_path, FILE_PATHS.config)


def resolve_on_integrity_failure() -> ConfigResolution:
    remove_stale_temp_file()
    valid_config_keys = get_keys_recursively(DEFAULT_CONFIG)
    try:
        config_data = json_file.load_json_data(FILE_PATHS.config)
        config_keys = get_keys_recursively(config_data)
    except Exception:
        capture("Config missing or unreadable, attempting restore from backup", level=LogLevel.WARNING)
        restore_last_known_good_config()
        remove_stale_backup_file()
        if not FILE_PATHS.config.exists():
            reset_to_default_config()
            return ConfigResolution(json_file.load_json_data(FILE_PATHS.config), is_fresh=True)
        try:
            config_data = json_file.load_json_data(FILE_PATHS.config)
            config_keys = get_keys_recursively(config_data)
        except Exception:
            capture("Config is unreadable after restore, resetting to defaults", level=LogLevel.WARNING)
            reset_to_default_config()
            return ConfigResolution(json_file.load_json_data(FILE_PATHS.config), is_fresh=True)
    else:
        remove_stale_backup_file()
    if valid_config(valid_config_keys, config_keys):
        capture("Config integrity check passed", level=LogLevel.DEBUG)
        return ConfigResolution(config_data, is_fresh=False)
    try:
        repair_config(FILE_PATHS.config, valid_config_keys, config_keys)
        capture("Config repair succeeded")
    except Exception:
        capture("Config repair failed, resetting to defaults", level=LogLevel.ERROR)
        reset_to_default_config()
    return ConfigResolution(json_file.load_json_data(FILE_PATHS.config), is_fresh=True)
