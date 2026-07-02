from PySide6.QtWidgets import QVBoxLayout, QWidget

from subsearch.runtime.config.defaults import ConfigKey
from subsearch.ui.cards.base import SettingsCard
from subsearch.ui.cards.descriptions import SETTING_DESCRIPTIONS, CardKey
from subsearch.ui.state.store import SettingsStore
from subsearch.ui.widgets.setting_rows import (
    SwitchRow,
    make_switches_mutually_exclusive,
)


class SubtitleHandlingCard(SettingsCard):
    def __init__(self, store: SettingsStore, parent: QWidget | None = None) -> None:
        super().__init__("Subtitle handling", store, parent=parent)
        self.store = store
        self.add_header_help(SETTING_DESCRIPTIONS[CardKey.SUBTITLE_HANDLING].explanation)

        self.body_layout.addWidget(self._build_automatic_handling())

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
