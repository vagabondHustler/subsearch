from typing import Any, Callable

from PySide6.QtCore import QObject, Signal

from subsearch.io.language_data import load_language_data
from subsearch.runtime.config import session as config_session
from subsearch.runtime.keys import ConfigKey


class SettingsStore(QObject):
    value_changed = Signal(str, object)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._session = config_session.get_config_session()

    def read(self, key: ConfigKey | str) -> Any:
        return self._session.read(key)

    def write(self, key: ConfigKey | str, value: Any) -> None:
        if self._session.read(key) == value:
            return
        self._session.write(key, value)
        self.value_changed.emit(str(key), value)

    def subscribe(self, key: ConfigKey | str, callback: Callable[[Any], None]) -> None:
        def relay_matching_key(changed_key: str, value: Any) -> None:
            if changed_key == key:
                callback(value)

        self.value_changed.connect(relay_matching_key)

    def commit(self) -> None:
        self._session.commit()

    def language_data(self) -> dict[str, Any]:
        return load_language_data()
