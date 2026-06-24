import copy
from pathlib import Path
from typing import Any

from subsearch.io import json_file
from subsearch.runtime.config import integrity
from subsearch.runtime.config.composition import FILE_PATHS
from subsearch.runtime.config.defaults import ConfigKey
from subsearch.runtime.config.mapper import get_app_config_from_data
from subsearch.runtime.config.nested_dict import (
    changed_leaves,
    read_nested_value,
    set_nested_value,
)
from subsearch.runtime.models import AppConfig
from subsearch.runtime.recorder import LogLevel, capture


class ConfigSession:
    def __init__(self, config_file_path: Path, initial_data: dict[str, Any], is_fresh: bool = False) -> None:
        self.config_file_path = config_file_path
        self.backup_file_path = config_file_path.with_suffix(f"{config_file_path.suffix}.bak")
        self.in_memory_data = initial_data
        self.is_fresh = is_fresh
        self.has_uncommitted_changes = False
        self.last_known_good_backed_up = False
        self.tracked_changes: dict[str, tuple[Any, Any]] = {}

    def read(self, key: ConfigKey | str) -> Any:
        return read_nested_value(self.in_memory_data, key)

    def snapshot(self) -> AppConfig:
        return get_app_config_from_data(copy.deepcopy(self.in_memory_data))

    def write(self, key: ConfigKey | str, value: Any | None) -> None:
        self.back_up_last_known_good()
        previous_value = read_nested_value(self.in_memory_data, key)
        set_nested_value(self.in_memory_data, key, value)
        self.has_uncommitted_changes = True

        for leaf_key, leaf_old, leaf_new in changed_leaves(key, previous_value, value):
            self.tracked_changes[leaf_key] = (leaf_old, leaf_new)

    def back_up_last_known_good(self) -> None:
        if self.last_known_good_backed_up:
            return None
        if self.config_file_path.exists():
            json_file.dump_json_data(self.backup_file_path, json_file.load_json_data(self.config_file_path))
        self.last_known_good_backed_up = True

    def commit(self) -> None:
        if not self.has_uncommitted_changes:
            return None
        json_file.dump_json_data(self.config_file_path, self.in_memory_data)
        self.log_tracked_changes()

        capture("Settings saved", level=LogLevel.DEBUG)
        self.has_uncommitted_changes = False
        self.backup_file_path.unlink(missing_ok=True)
        self.last_known_good_backed_up = False

    def log_tracked_changes(self) -> None:
        for key, (old_value, new_value) in self.tracked_changes.items():
            capture(f"Config change: {key}: {old_value!r} → {new_value!r}", level=LogLevel.DEBUG)
        self.tracked_changes.clear()

    def revert(self) -> None:
        capture("Discarded unsaved settings", level=LogLevel.WARNING)
        self.in_memory_data = json_file.load_json_data(self.config_file_path)
        self.has_uncommitted_changes = False
        self.tracked_changes.clear()


_active_config_session: ConfigSession | None = None


def read_config_value(key: ConfigKey | str) -> Any:
    if _active_config_session is not None:
        return _active_config_session.read(key)
    return json_file.load_json_value(FILE_PATHS.config, key)


def diagnostics_enabled() -> bool:
    if _active_config_session is None:
        return False
    return bool(_active_config_session.read(ConfigKey.DIAGNOSTICS_ENABLED))


def get_config_session() -> ConfigSession:
    global _active_config_session
    if _active_config_session is None:
        resolution = integrity.resolve_on_integrity_failure()
        _active_config_session = ConfigSession(FILE_PATHS.config, resolution.config_data, resolution.is_fresh)
    return _active_config_session


def reset_config_session() -> None:
    global _active_config_session
    _active_config_session = None
