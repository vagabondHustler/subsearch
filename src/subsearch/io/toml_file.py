import copy
import functools
import os
from pathlib import Path
from typing import Any

import toml

from subsearch.runtime.config.constants import DEFAULT_CONFIG, FILE_PATHS
from subsearch.runtime.logging import log_sanitizer
from subsearch.runtime.logging.logger import log
from subsearch.runtime.models.model import AppConfig


def load_toml_data(toml_file_path: Path) -> dict[str, Any]:
    log.debug(f"Read toml file from {toml_file_path.name}")
    with open(toml_file_path, "r") as f:
        return toml.load(f)


@functools.lru_cache(maxsize=None)
def _load_language_data_cached(toml_file_path: Path) -> dict[str, Any]:
    return load_toml_data(toml_file_path)


def load_language_data() -> dict[str, Any]:
    return _load_language_data_cached(FILE_PATHS.subtitle_languages)


def load_toml_value(toml_file_path: Path, key: str) -> Any:
    toml_data = load_toml_data(toml_file_path)
    keys = key.split(".")
    value = functools.reduce(dict.get, keys, toml_data)  # type: ignore
    return value


def dump_toml_data(toml_file_path: Path, toml_data: dict) -> None:
    temp_file_path = toml_file_path.with_suffix(f"{toml_file_path.suffix}.tmp")
    try:
        with open(temp_file_path, "w") as file:
            toml.dump(toml_data, file)
            file.flush()
            os.fsync(file.fileno())
        os.replace(temp_file_path, toml_file_path)

        log.debug(f"Wrote config to {toml_file_path.name}")
    except Exception as e:
        log.error(f"Failed to write config to {toml_file_path.name}: {e}")
        raise


def set_nested_value(toml_data: dict, key: str, value: Any | None) -> None:
    keys = key.split(".")
    functools.reduce(dict.get, keys[:-1], toml_data)[keys[-1]] = value  # type: ignore


def descend_into(node: Any, key: str) -> Any:
    return node.get(key) if isinstance(node, dict) else None


def read_nested_value(toml_data: dict, key: str) -> Any:
    keys = key.split(".")
    return functools.reduce(descend_into, keys, toml_data)


def delete_nested_value(toml_data: dict, key: str) -> None:
    keys = key.split(".")
    parent = functools.reduce(descend_into, keys[:-1], toml_data)
    if isinstance(parent, dict):
        parent.pop(keys[-1], None)


def update_toml_key(toml_file_path: Path, key: str, value: Any | None) -> None:
    toml_data = load_toml_data(toml_file_path)
    set_nested_value(toml_data, key, value)
    dump_toml_data(toml_file_path, toml_data)


def del_toml_key(toml_file_path: Path, key: str) -> None:
    toml_data = load_toml_data(toml_file_path)
    delete_nested_value(toml_data, key)
    dump_toml_data(toml_file_path, toml_data)


def repair_toml_config(toml_file_path: Path, valid_config_keys: list[str], config_keys: list[str]) -> None:
    log.warning("Config schema mismatch , repairing")
    toml_data = load_toml_data(toml_file_path)

    obsolete_keys = [key for key in config_keys if key not in valid_config_keys]
    for key in obsolete_keys:
        log.info(f"Removing obsolete config key {key}")
        delete_nested_value(toml_data, key)

    missing_keys = [key for key in valid_config_keys if key not in config_keys]
    for key in missing_keys:
        log.info(f"Adding missing config key {key}")
        keys = key.split(".")
        value = functools.reduce(dict.get, keys, DEFAULT_CONFIG)  # type: ignore
        set_nested_value(toml_data, key, value)

    dump_toml_data(toml_file_path, toml_data)


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


def remove_stale_temp_file() -> None:
    temp_file_path = FILE_PATHS.config.with_suffix(f"{FILE_PATHS.config.suffix}.tmp")
    temp_file_path.unlink(missing_ok=True)


def remove_stale_backup_file() -> None:
    backup_file_path = FILE_PATHS.config.with_suffix(f"{FILE_PATHS.config.suffix}.bak")
    backup_file_path.unlink(missing_ok=True)


def reset_to_default_config() -> None:
    log.warning(f"Resetting config to defaults at {FILE_PATHS.config}")
    FILE_PATHS.config.unlink(missing_ok=True)
    dump_toml_data(FILE_PATHS.config, DEFAULT_CONFIG)


def resolve_on_integrity_failure() -> dict[str, Any]:
    remove_stale_temp_file()
    valid_config_keys = get_keys_recursively(DEFAULT_CONFIG)
    try:
        toml_data = load_toml_data(FILE_PATHS.config)
        config_keys = get_keys_recursively(toml_data)
    except Exception:
        log.warning("Config missing or unreadable , attempting restore from backup")
        restore_last_known_good_config()
        remove_stale_backup_file()
        if not FILE_PATHS.config.exists():
            reset_to_default_config()
            return load_toml_data(FILE_PATHS.config)
        try:
            toml_data = load_toml_data(FILE_PATHS.config)
            config_keys = get_keys_recursively(toml_data)
        except Exception:
            log.warning("Config is unreadable after restore , resetting to defaults")
            reset_to_default_config()
            return load_toml_data(FILE_PATHS.config)
    else:
        remove_stale_backup_file()
    if valid_config(valid_config_keys, config_keys):
        log.debug("Config integrity check passed")
        return toml_data
    try:
        repair_toml_config(FILE_PATHS.config, valid_config_keys, config_keys)
        log.info("Config repair succeeded")
    except Exception:
        log.error("Config repair failed , resetting to defaults")
        reset_to_default_config()
    return load_toml_data(FILE_PATHS.config)


def get_app_config_from_data(data: dict[str, Any]) -> AppConfig:
    return AppConfig(
        selected_language=data["language"]["selected"],
        accept_threshold=data["search"]["accept_threshold"],
        hearing_impaired=data["search"]["hearing_impaired"],
        non_hearing_impaired=data["search"]["non_hearing_impaired"],
        only_foreign_parts=data["search"]["only_foreign_parts"],
        providers=data["search"]["providers"],
        token_weights=data["search"]["token_weights"],
        token_multipliers=data["search"]["token_multipliers"],
        context_menu=data["shell_integration"]["context_menu"],
        context_menu_icon=data["shell_integration"]["context_menu_icon"],
        file_extensions=data["shell_integration"]["file_extensions"],
        system_tray=data["notifications"]["system_tray"],
        summary_notification=data["notifications"]["summary_notification"],
        automatic_downloads=data["download"]["automatic"],
        always_open_manager=data["download"]["always_open_manager"],
        open_manager_on_no_matches=data["download"]["open_manager_on_no_matches"],
        post_processing=data["post_processing"],
        show_terminal=data["application"]["show_terminal"],
        single_instance=data["application"]["single_instance"],
        api_call_limit=data["network"]["api_call_limit"],
        request_connect_timeout=data["network"]["request_connect_timeout"],
        request_read_timeout=data["network"]["request_read_timeout"],
        diagnostics=data["diagnostics"],
        subsource_api_key_exists=data["credentials"]["subsource"]["api_key_exists"],
        subsource_api_key=data["credentials"]["subsource"]["api_key"],
    )


def get_app_config(toml_file_path: Path) -> AppConfig:
    return get_app_config_from_data(load_toml_data(toml_file_path))


class ConfigSession:
    def __init__(self, toml_file_path: Path, initial_data: dict[str, Any]) -> None:
        self.toml_file_path = toml_file_path
        self.backup_file_path = toml_file_path.with_suffix(f"{toml_file_path.suffix}.bak")
        self.in_memory_data = initial_data
        self.has_uncommitted_changes = False
        self.last_known_good_backed_up = False

    def read(self, key: str) -> Any:
        return read_nested_value(self.in_memory_data, key)

    def snapshot(self) -> AppConfig:
        return get_app_config_from_data(copy.deepcopy(self.in_memory_data))

    def write(self, key: str, value: Any | None) -> None:
        self.back_up_last_known_good()
        set_nested_value(self.in_memory_data, key, value)
        self.has_uncommitted_changes = True

        sanitized_value = log_sanitizer.sanitize(repr(value))
        log.debug(f"In-memory config change: {key} = {sanitized_value}")

    def back_up_last_known_good(self) -> None:
        if self.last_known_good_backed_up:
            return None
        if self.toml_file_path.exists():
            dump_toml_data(self.backup_file_path, load_toml_data(self.toml_file_path))
        self.last_known_good_backed_up = True

    def commit(self) -> None:
        if not self.has_uncommitted_changes:
            return None
        dump_toml_data(self.toml_file_path, self.in_memory_data)

        log.debug(f"Config session committed to {self.toml_file_path}")
        self.has_uncommitted_changes = False
        self.backup_file_path.unlink(missing_ok=True)
        self.last_known_good_backed_up = False

    def revert(self) -> None:
        log.warning("Reverting uncommitted config changes")
        self.in_memory_data = load_toml_data(self.toml_file_path)
        self.has_uncommitted_changes = False


_active_config_session: ConfigSession | None = None


def diagnostics_enabled() -> bool:
    if _active_config_session is None:
        return False
    return bool(_active_config_session.read("diagnostics.enabled"))


def restore_last_known_good_config() -> None:
    backup_file_path = FILE_PATHS.config.with_suffix(f"{FILE_PATHS.config.suffix}.bak")
    if not backup_file_path.exists():
        return None
    log.info(f"Restoring last known good config from {backup_file_path}")
    os.replace(backup_file_path, FILE_PATHS.config)


def get_config_session() -> ConfigSession:
    global _active_config_session
    if _active_config_session is None:
        toml_data = resolve_on_integrity_failure()
        _active_config_session = ConfigSession(FILE_PATHS.config, toml_data)
    return _active_config_session


def reset_config_session() -> None:
    global _active_config_session
    _active_config_session = None
