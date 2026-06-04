import copy
import functools
import os
from pathlib import Path
from typing import Any

import toml

from subsearch.runtime.logger import log
from subsearch.runtime.constants import DEFAULT_CONFIG, FILE_PATHS
from subsearch.runtime.model import AppConfig


def load_toml_data(toml_file_path: Path) -> dict[str, Any]:
    with open(toml_file_path, "r") as f:
        return toml.load(f)


def load_toml_value(toml_file_path: Path, key: str) -> Any:
    toml_data = load_toml_data(toml_file_path)
    keys = key.split(".")
    value = functools.reduce(dict.get, keys, toml_data)  # type: ignore
    return value


def dump_toml_data(toml_file_path: Path, toml_data: dict) -> None:
    temp_file_path = toml_file_path.with_suffix(f"{toml_file_path.suffix}.tmp")
    with open(temp_file_path, "w") as file:
        toml.dump(toml_data, file)
        file.flush()
        os.fsync(file.fileno())
    os.replace(temp_file_path, toml_file_path)


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
    log.debug(f"Reparing config")
    toml_data = load_toml_data(toml_file_path)

    obsolete_keys = [key for key in config_keys if key not in valid_config_keys]
    for key in obsolete_keys:
        log.debug(f"Removing obsolete key {key}")
        delete_nested_value(toml_data, key)

    missing_keys = [key for key in valid_config_keys if key not in config_keys]
    for key in missing_keys:
        log.debug(f"Adding missing key {key}")
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
    log.debug(f"Creating default config at {FILE_PATHS.config}")
    FILE_PATHS.config.unlink(missing_ok=True)
    dump_toml_data(FILE_PATHS.config, DEFAULT_CONFIG)


def config_is_readable() -> bool:
    try:
        load_toml_data(FILE_PATHS.config)
        return True
    except Exception:
        return False


def resolve_on_integrity_failure() -> None:
    remove_stale_temp_file()
    if not FILE_PATHS.config.exists() or not config_is_readable():
        restore_last_known_good_config()
    else:
        remove_stale_backup_file()
    if not FILE_PATHS.config.exists():
        reset_to_default_config()
        return None
    valid_config_keys = get_keys_recursively(DEFAULT_CONFIG)
    try:
        config_keys = get_keys_recursively(load_toml_data(FILE_PATHS.config))
    except Exception:
        log.debug(f"Config is unreadable")
        reset_to_default_config()
        return None
    if valid_config(valid_config_keys, config_keys):
        log.debug(f"Config is valid")
        return None
    try:
        log.debug(f"Config not valid")
        repair_toml_config(FILE_PATHS.config, valid_config_keys, config_keys)
        log.debug(f"Repair succeeded")
    except Exception:
        log.debug(f"Repair faild")
        reset_to_default_config()


def get_app_config_from_data(data: dict[str, Any]) -> AppConfig:
    return AppConfig(
        selected_language=data["language"]["selected"],
        accept_threshold=data["search"]["accept_threshold"],
        hearing_impaired=data["search"]["hearing_impaired"],
        non_hearing_impaired=data["search"]["non_hearing_impaired"],
        only_foreign_parts=data["search"]["only_foreign_parts"],
        providers=data["search"]["providers"],
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
        subsource_api_key=data["credentials"]["subsource_api_key"],
    )


def get_app_config(toml_file_path: Path) -> AppConfig:
    return get_app_config_from_data(load_toml_data(toml_file_path))


class ConfigSession:
    def __init__(self, toml_file_path: Path) -> None:
        self.toml_file_path = toml_file_path
        self.backup_file_path = toml_file_path.with_suffix(f"{toml_file_path.suffix}.bak")
        self.in_memory_data = load_toml_data(toml_file_path)
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
        self.has_uncommitted_changes = False
        self.backup_file_path.unlink(missing_ok=True)
        self.last_known_good_backed_up = False

    def revert(self) -> None:
        self.in_memory_data = load_toml_data(self.toml_file_path)
        self.has_uncommitted_changes = False


_active_config_session: ConfigSession | None = None


def restore_last_known_good_config() -> None:
    backup_file_path = FILE_PATHS.config.with_suffix(f"{FILE_PATHS.config.suffix}.bak")
    if not backup_file_path.exists():
        return None
    log.debug(f"Restoring last known good config from {backup_file_path}")
    os.replace(backup_file_path, FILE_PATHS.config)


def get_config_session() -> ConfigSession:
    global _active_config_session
    if _active_config_session is None:
        _active_config_session = ConfigSession(FILE_PATHS.config)
    return _active_config_session


def reset_config_session() -> None:
    global _active_config_session
    _active_config_session = None
