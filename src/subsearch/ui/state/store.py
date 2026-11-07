from typing import Any, Callable

from PySide6.QtCore import QObject, QTimer, Signal

from subsearch.io.language_data import load_language_data
from subsearch.runtime.config import PATH_RESOLVER
from subsearch.runtime.config import session as config_session
from subsearch.runtime.config.defaults import ConfigKey
from subsearch.runtime.recorder import LogLevel, capture

AUTO_SAVE_INTERVAL_MS = 5000


class SettingsStore(QObject):
    value_changed = Signal(str, object)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._session = config_session.get_config_session()
        self._auto_save_timer = QTimer(self)
        self._auto_save_timer.setInterval(AUTO_SAVE_INTERVAL_MS)
        self._auto_save_timer.timeout.connect(self.flush)
        self._auto_save_timer.start()

    def read(self, key: ConfigKey | str) -> Any:
        return self._session.read(key)

    def write(self, key: ConfigKey | str, value: Any) -> None:
        if self._session.read(key) == value:
            return
        self._session.write(key, value)
        self.value_changed.emit(str(key), value)

    def flush(self) -> None:
        if not self._session.has_uncommitted_changes:
            return
        capture("Auto-saving settings", level=LogLevel.DEBUG)
        self._session.commit()

    def subscribe(self, key: ConfigKey | str, callback: Callable[[Any], None]) -> None:
        def relay_matching_key(changed_key: str, value: Any) -> None:
            if changed_key == key:
                callback(value)

        self.value_changed.connect(relay_matching_key)

    def resolved_default_directory(self, key: ConfigKey | str) -> str:
        defaults_by_key = {
            ConfigKey.PATHS_DOWNLOAD_DIRECTORY: PATH_RESOLVER.default_download_directory,
            ConfigKey.PATHS_EXTRACTION_DIRECTORY: PATH_RESOLVER.default_extraction_directory,
        }
        resolve_default = defaults_by_key.get(ConfigKey(key))
        return str(resolve_default()) if resolve_default is not None else ""

    def language_data(self) -> dict[str, Any]:
        return load_language_data()
