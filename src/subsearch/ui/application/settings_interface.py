from collections.abc import Sequence
from typing import Callable

from PySide6.QtCore import Qt
from PySide6.QtGui import QShowEvent
from PySide6.QtWidgets import QVBoxLayout, QWidget
from qfluentwidgets import SingleDirectionScrollArea

from subsearch.ui.cards import SettingsCard


def _collapsible(*cards: SettingsCard) -> list[SettingsCard]:
    for card in cards:
        card.make_collapsible()
    return list(cards)


class SettingsInterface(SingleDirectionScrollArea):
    def __init__(self, object_name: str, build_cards: Callable[[], Sequence[QWidget]]) -> None:
        super().__init__(orient=Qt.Orientation.Vertical)
        self.setObjectName(object_name)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._build_cards = build_cards
        self._cards_built = False

        self._container = QWidget(self)
        self._layout = QVBoxLayout(self._container)
        self._layout.setContentsMargins(36, 24, 36, 24)
        self._layout.setSpacing(16)
        self._layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.setWidget(self._container)
        self.enableTransparentBackground()

    def showEvent(self, event: QShowEvent) -> None:
        self.build_cards()
        super().showEvent(event)

    def build_cards(self) -> None:
        if self._cards_built:
            return
        self._cards_built = True
        for card in self._build_cards():
            self._layout.addWidget(card)
