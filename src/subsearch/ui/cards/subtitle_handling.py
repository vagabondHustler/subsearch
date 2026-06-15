from PySide6.QtWidgets import QVBoxLayout, QWidget

from subsearch.runtime.keys import CardKey, ConfigKey
from subsearch.ui.cards.base import SettingsCard
from subsearch.ui.cards.descriptions import SETTING_DESCRIPTIONS
from subsearch.ui.state.store import SettingsStore
from subsearch.ui.theme.separators import make_fading_separator
from subsearch.ui.widgets.setting_rows import (
    SwitchRow,
    make_switches_mutually_exclusive,
)


class SubtitleHandlingCard(SettingsCard):
    def __init__(self, store: SettingsStore, parent: QWidget | None = None) -> None:
        super().__init__("Subtitle handling", store, parent=parent)
        self.store = store
        self.add_header_help(SETTING_DESCRIPTIONS[CardKey.SUBTITLE_HANDLING].explanation)

        self._automatic_handling = self._build_automatic_handling()
        self.body_layout.addWidget(self._automatic_handling)

        self.body_layout.addWidget(make_fading_separator(opacity=0.6, width_fraction=0.75, vertical_margin=8))

        self.add_row(SwitchRow(ConfigKey.SUBTITLE_WORKSPACE_MANUAL_POST_PROCESSING, store))

        self._apply_manual_handle_state(bool(store.read(ConfigKey.SUBTITLE_WORKSPACE_MANUAL_POST_PROCESSING)))
        store.value_changed.connect(self._on_store_changed)

    def _build_automatic_handling(self) -> QWidget:
        container = QWidget(self)
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        rename = SwitchRow(ConfigKey.POST_PROCESSING_RENEAME, self.store)
        self.move_best = SwitchRow(ConfigKey.POST_PROCESSING_MOVE_BEST, self.store)
        self.move_all = SwitchRow(ConfigKey.POST_PROCESSING_MOVE_ALL, self.store)
        layout.addWidget(rename)
        layout.addWidget(self.move_best)
        layout.addWidget(self.move_all)
        for row in (rename, self.move_best, self.move_all):
            self.register_restore_defaults([(row.config_key, row.default_value)])
        make_switches_mutually_exclusive(self.move_best, self.move_all)
        return container

    def _on_store_changed(self, key: str, value: object) -> None:
        if key == ConfigKey.SUBTITLE_WORKSPACE_MANUAL_POST_PROCESSING:
            self._apply_manual_handle_state(bool(value))

    def _apply_manual_handle_state(self, manual_enabled: bool) -> None:
        self._automatic_handling.setEnabled(not manual_enabled)
