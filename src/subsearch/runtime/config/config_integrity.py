import functools
import os
from pathlib import Path
from typing import Any

from subsearch.io import json_file
from subsearch.io.nested_dict import (
    delete_nested_value,
    get_keys_recursively,
    set_nested_value,
)
from subsearch.runtime.config.constants import DEFAULT_CONFIG, FILE_PATHS
from subsearch.runtime.logging.logger import log


class ConfigResolution:
    def __init__(self, config_data: dict[str, Any], is_fresh: bool) -> None:
        self.config_data = config_data
        self.is_fresh = is_fresh


def repair_config(config_file_path: Path, valid_config_keys: list[str], config_keys: list[str]) -> None:
    log.warning("Config schema mismatch , repairing")
    config_data = json_file.load_json_data(config_file_path)

    obsolete_keys = [key for key in config_keys if key not in valid_config_keys]
    for key in obsolete_keys:
        log.info(f"Removing obsolete config key {key}")
        delete_nested_value(config_data, key)

    missing_keys = [key for key in valid_config_keys if key not in config_keys]
    for key in missing_keys:
        log.info(f"Adding missing config key {key}")
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
    log.warning(f"Resetting config to defaults at {FILE_PATHS.config}")
    FILE_PATHS.config.unlink(missing_ok=True)
    json_file.dump_json_data(FILE_PATHS.config, DEFAULT_CONFIG)


def restore_last_known_good_config() -> None:
    backup_file_path = FILE_PATHS.config.with_suffix(f"{FILE_PATHS.config.suffix}.bak")
    if not backup_file_path.exists():
        return None
    log.info(f"Restoring last known good config from {backup_file_path}")
    os.replace(backup_file_path, FILE_PATHS.config)


def migrate_download_section(config_data: dict[str, Any]) -> bool:
    if "download" not in config_data:
        return False
    old = config_data.pop("download")
    automatic = old.get("automatic", True)
    always_open = old.get("always_open_manager", False)
    if not automatic:
        search_mode = "manual"
    elif always_open:
        search_mode = "hybrid"
    else:
        search_mode = "automatic"
    config_data.setdefault("download_manager", {})["search_mode"] = search_mode
    log.info(f"Migrated download config to download_manager.search_mode = {search_mode}")
    return True


def migrate_unified_download_destination(config_data: dict[str, Any]) -> bool:
    download_manager = config_data.get("download_manager", {})
    stale_keys = [key for key in ("use_post_processing_target", "target_path") if key in download_manager]
    if not stale_keys:
        return False
    for key in stale_keys:
        download_manager.pop(key)
    log.info(f"Removed stale download_manager keys now unified with post_processing: {stale_keys}")
    return True


def migrate_token_multipliers(config_data: dict[str, Any]) -> bool:
    multipliers = config_data.get("search", {}).get("token_multipliers")
    if not multipliers:
        return False
    # Old format stored a 0-100 integer penalty; the new format stores the multiplier float directly.
    if not any(isinstance(value, int) for value in multipliers.values()):
        return False
    converted = {token: (100 - penalty) / 100 for token, penalty in multipliers.items()}
    config_data["search"]["token_multipliers"] = converted
    log.info(f"Migrated token multipliers from penalty integers to multiplier floats: {converted}")
    return True


def migrate_api_call_limit(config_data: dict[str, Any]) -> bool:
    network = config_data.get("network", {})
    if "api_call_limit" not in network:
        return False
    limit = network.pop("api_call_limit")
    config_data.setdefault("search", {})["downloads_per_provider"] = limit
    log.info(f"Migrated network.api_call_limit to search.downloads_per_provider = {limit}")
    return True


def resolve_on_integrity_failure() -> ConfigResolution:
    remove_stale_temp_file()
    valid_config_keys = get_keys_recursively(DEFAULT_CONFIG)
    try:
        config_data = json_file.load_json_data(FILE_PATHS.config)
        config_keys = get_keys_recursively(config_data)
    except Exception:
        log.warning("Config missing or unreadable, attempting restore from backup")
        restore_last_known_good_config()
        remove_stale_backup_file()
        if not FILE_PATHS.config.exists():
            reset_to_default_config()
            return ConfigResolution(json_file.load_json_data(FILE_PATHS.config), is_fresh=True)
        try:
            config_data = json_file.load_json_data(FILE_PATHS.config)
            config_keys = get_keys_recursively(config_data)
        except Exception:
            log.warning("Config is unreadable after restore, resetting to defaults")
            reset_to_default_config()
            return ConfigResolution(json_file.load_json_data(FILE_PATHS.config), is_fresh=True)
    else:
        remove_stale_backup_file()
    migrated_download = migrate_download_section(config_data)
    migrated_destination = migrate_unified_download_destination(config_data)
    migrated_multipliers = migrate_token_multipliers(config_data)
    migrated_api_call_limit = migrate_api_call_limit(config_data)
    if migrated_download or migrated_destination or migrated_multipliers or migrated_api_call_limit:
        json_file.dump_json_data(FILE_PATHS.config, config_data)
        config_keys = get_keys_recursively(config_data)
    if valid_config(valid_config_keys, config_keys):
        log.debug("Config integrity check passed")
        return ConfigResolution(config_data, is_fresh=False)
    try:
        repair_config(FILE_PATHS.config, valid_config_keys, config_keys)
        log.info("Config repair succeeded")
    except Exception:
        log.error("Config repair failed, resetting to defaults")
        reset_to_default_config()
    return ConfigResolution(json_file.load_json_data(FILE_PATHS.config), is_fresh=True)
