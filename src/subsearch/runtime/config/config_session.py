import copy
from pathlib import Path
from typing import Any

from subsearch.io import toml_file
from subsearch.io.nested_dict import changed_leaves, read_nested_value, set_nested_value
from subsearch.runtime.config import config_integrity
from subsearch.runtime.config.app_config_mapper import get_app_config_from_data
from subsearch.runtime.config.constants import FILE_PATHS
from subsearch.runtime.logging.logger import log
from subsearch.runtime.models.model import AppConfig


class ConfigSession:
    def __init__(self, toml_file_path: Path, initial_data: dict[str, Any], is_fresh: bool = False) -> None:
        self.toml_file_path = toml_file_path
        self.backup_file_path = toml_file_path.with_suffix(f"{toml_file_path.suffix}.bak")
        self.in_memory_data = initial_data
        self.is_fresh = is_fresh
        self.has_uncommitted_changes = False
        self.last_known_good_backed_up = False
        self.tracked_changes: dict[str, Any] = {}

    def read(self, key: str) -> Any:
        return read_nested_value(self.in_memory_data, key)

    def snapshot(self) -> AppConfig:
        return get_app_config_from_data(copy.deepcopy(self.in_memory_data))

    def write(self, key: str, value: Any | None) -> None:
        self.back_up_last_known_good()
        previous_value = read_nested_value(self.in_memory_data, key)
        set_nested_value(self.in_memory_data, key, value)
        self.has_uncommitted_changes = True

        for leaf_key, leaf_value in changed_leaves(key, previous_value, value):
            self.tracked_changes[leaf_key] = leaf_value

    def back_up_last_known_good(self) -> None:
        if self.last_known_good_backed_up:
            return None
        if self.toml_file_path.exists():
            toml_file.dump_toml_data(self.backup_file_path, toml_file.load_toml_data(self.toml_file_path))
        self.last_known_good_backed_up = True

    def commit(self) -> None:
        if not self.has_uncommitted_changes:
            return None
        toml_file.dump_toml_data(self.toml_file_path, self.in_memory_data)
        self.log_tracked_changes()

        log.debug(f"Config session committed to {self.toml_file_path.name}")
        self.has_uncommitted_changes = False
        self.backup_file_path.unlink(missing_ok=True)
        self.last_known_good_backed_up = False

    def log_tracked_changes(self) -> None:
        for key, value in self.tracked_changes.items():
            log.debug(f"Config change: {key}={value!r}")
        self.tracked_changes.clear()

    def revert(self) -> None:
        log.warning("Reverting uncommitted config changes")
        self.in_memory_data = toml_file.load_toml_data(self.toml_file_path)
        self.has_uncommitted_changes = False
        self.tracked_changes.clear()


_active_config_session: ConfigSession | None = None


def read_config_value(key: str) -> Any:
    if _active_config_session is not None:
        return _active_config_session.read(key)
    return toml_file.load_toml_value(FILE_PATHS.config, key)


def diagnostics_enabled() -> bool:
    if _active_config_session is None:
        return False
    return bool(_active_config_session.read("diagnostics.enabled"))


def get_config_session() -> ConfigSession:
    global _active_config_session
    if _active_config_session is None:
        resolution = config_integrity.resolve_on_integrity_failure()
        _active_config_session = ConfigSession(FILE_PATHS.config, resolution.toml_data, resolution.is_fresh)
    return _active_config_session


def reset_config_session() -> None:
    global _active_config_session
    _active_config_session = None
