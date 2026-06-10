from typing import Any, Callable

from PySide6.QtCore import QObject, Signal

from subsearch.io import toml_file


class SettingsStore(QObject):
    value_changed = Signal(str, object)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._session = toml_file.get_config_session()

    def read(self, key: str) -> Any:
        return self._session.read(key)

    def write(self, key: str, value: Any) -> None:
        self._session.write(key, value)
        self.value_changed.emit(key, value)

    def subscribe(self, key: str, callback: Callable[[Any], None]) -> None:
        def relay_matching_key(changed_key: str, value: Any) -> None:
            if changed_key == key:
                callback(value)

        self.value_changed.connect(relay_matching_key)

    def commit(self) -> None:
        self._session.commit()

    def language_data(self) -> dict[str, Any]:
        return toml_file.load_language_data()
