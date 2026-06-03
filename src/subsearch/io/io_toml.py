import functools
from pathlib import Path
from typing import Any, Union

import toml

from subsearch.logger import log
from subsearch.runtime.constants import DEFAULT_CONFIG, FILE_PATHS
from subsearch.model import AppConfig


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
    log.stdout(f"Reparing config", level="debug")
    obsolete_keys = [key for key in config_keys if key not in valid_config_keys]
    for key in obsolete_keys:
        log.stdout(f"Removing obsolete key {key}", level="debug")
        del_toml_key(toml_file_path, key)

    missing_keys = [key for key in valid_config_keys if key not in config_keys]
    for key in missing_keys:
        log.stdout(f"Adding missing key {key}", level="debug")
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
        log.stdout(f"No config.toml exsist, creating default at {FILE_PATHS.config}", level="debug")
        dump_toml_data(FILE_PATHS.config, DEFAULT_CONFIG)
        return None
    valid_config_keys = get_keys_recursively(DEFAULT_CONFIG)
    config_keys = get_keys_recursively(load_toml_data(FILE_PATHS.config))
    valid = valid_config(valid_config_keys, config_keys)
    if valid:
        log.stdout(f"Config is valid", level="debug")
        return None
    try:
        log.stdout(f"Config not valid", level="debug")
        repair_toml_config(FILE_PATHS.config, valid_config_keys, config_keys)
    except Exception:
        log.stdout(f"Repair faild, creating default at {FILE_PATHS.config}", level="debug")
        FILE_PATHS.config.unlink()
        dump_toml_data(FILE_PATHS.config, DEFAULT_CONFIG)
    log.stdout(f"Repair succeeded", level="debug")


def get_app_config(toml_file_path: Path) -> AppConfig:
    data = load_toml_data(toml_file_path)
    user_data = AppConfig(
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
    )
    return user_data
