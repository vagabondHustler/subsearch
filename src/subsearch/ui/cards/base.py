from typing import Protocol, runtime_checkable

from PySide6.QtCore import QSize, QTimer
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget
from qfluentwidgets import BodyLabel, HeaderCardWidget, TransparentToolButton

from subsearch.runtime.keys import CardKey, ConfigKey
from subsearch.ui.icons.lucide import LucideIcon, lucide_qicon
from subsearch.ui.state.store import SettingsStore
from subsearch.ui.theme import palette
from subsearch.ui.theme.metrics import (
    CARD_CONTENT_INSET,
    ROW_INSET,
    SMALL_ICON_SIZE,
    TOOL_BUTTON_SIZE,
)
from subsearch.ui.theme.separators import make_fading_separator
from subsearch.ui.theme.typography import apply_body_font, apply_title_font
from subsearch.ui.widgets.setting_rows import (
    DefaultsMap,
    HelpButton,
    RestoreDefaultsButton,
)

CARD_PANEL_OPACITY = 0.4
CARD_FILL_COLOR = QColor(255, 255, 255, 13)
CARD_BORDER_COLOR = QColor(0, 0, 0, 48)
CARD_BORDER_RADIUS = 6.0


@runtime_checkable
class RestorableRow(Protocol):
    config_key: ConfigKey
    default_value: object


def build_section_header(config_key: ConfigKey | CardKey, parent: QWidget) -> QHBoxLayout:
    from subsearch.ui.cards.descriptions import SETTING_DESCRIPTIONS

    description = SETTING_DESCRIPTIONS[config_key]
    title_label = BodyLabel(description.title, parent)
    apply_body_font(title_label)
    help_button = HelpButton(description.explanation, parent)
    header = QHBoxLayout()
    header.setContentsMargins(CARD_CONTENT_INSET, 10, ROW_INSET, 4)
    header.addWidget(title_label, stretch=1)
    header.addWidget(help_button)
    return header


def _make_button_placeholder(parent: QWidget) -> QWidget:
    placeholder = QWidget(parent)
    placeholder.setFixedSize(QSize(TOOL_BUTTON_SIZE, TOOL_BUTTON_SIZE))
    return placeholder


class SettingsCard(HeaderCardWidget):
    def __init__(  # pyright: ignore[reportIncompatibleVariableOverride]
        self,
        title: str,
        store: SettingsStore | None = None,
        show_restore_button: bool = True,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setTitle(title)
        apply_title_font(self.headerLabel)
        self._replace_header_separator()
        self.headerLayout.setContentsMargins(ROW_INSET, 0, ROW_INSET, 0)
        self.viewLayout.setContentsMargins(0, 8, 0, 8)
        self.body_layout = QVBoxLayout()
        self.body_layout.setContentsMargins(0, 0, 0, 0)
        self.body_layout.setSpacing(4)
        self.viewLayout.addLayout(self.body_layout)
        self._restore_store = store
        self._collected_defaults: DefaultsMap = []

        # Reserve fixed slots: stretch → search slot → restore slot → help slot.
        # Placeholders keep all positions stable whether or not each button is present.
        self.headerLayout.addStretch(1)
        self._search_slot = _make_button_placeholder(self)
        self.headerLayout.addWidget(self._search_slot)
        self._restore_slot = _make_button_placeholder(self)
        self.headerLayout.addWidget(self._restore_slot)
        self._help_slot = _make_button_placeholder(self)
        self.headerLayout.addWidget(self._help_slot)

        if not show_restore_button:
            self._restore_slot.hide()
        elif store is not None:
            # Deferred so subclasses can register defaults in their __init__ first.
            # `self` as context cancels the callback if the card is destroyed before
            # the event loop runs it (e.g. short-lived cards in tests).
            QTimer.singleShot(0, self, self._wire_restore_button)

    def paintEvent(self, e) -> None:
        painter = QPainter(self)
        painter.setRenderHints(QPainter.RenderHint.Antialiasing)
        painter.setOpacity(CARD_PANEL_OPACITY)
        painter.setBrush(CARD_FILL_COLOR)
        painter.setPen(CARD_BORDER_COLOR)
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), CARD_BORDER_RADIUS, CARD_BORDER_RADIUS)

    def _replace_header_separator(self) -> None:
        index = self.vBoxLayout.indexOf(self.separator)
        self.separator.hide()
        self.vBoxLayout.removeWidget(self.separator)
        self._header_separator = make_fading_separator()
        self.vBoxLayout.insertWidget(index, self._header_separator)

    def make_collapsible(self, collapsed: bool = False) -> None:
        self._collapse_button = TransparentToolButton(self)
        self._collapse_button.setFixedSize(TOOL_BUTTON_SIZE, TOOL_BUTTON_SIZE)
        self._collapse_button.setIconSize(QSize(SMALL_ICON_SIZE, SMALL_ICON_SIZE))
        self._collapse_button.clicked.connect(self._toggle_collapsed)
        self.headerLayout.insertWidget(0, self._collapse_button)
        self.set_collapsed(collapsed)

    def set_collapsed(self, collapsed: bool) -> None:
        self.view.setVisible(not collapsed)
        self._header_separator.setVisible(not collapsed)
        icon = LucideIcon.CHEVRON_RIGHT if collapsed else LucideIcon.CHEVRON_DOWN
        self._collapse_button.setIcon(lucide_qicon(icon, palette.NEUTRAL_3))
        self._collapse_button.setToolTip("Expand" if collapsed else "Collapse")

    def set_body_enabled(self, enabled: bool) -> None:
        self.view.setEnabled(enabled)

    def is_collapsed(self) -> bool:
        # isHidden (not isVisible) so the answer is right before the card is first shown.
        return self.view.isHidden()

    def _toggle_collapsed(self) -> None:
        self.set_collapsed(not self.is_collapsed())

    def _wire_restore_button(self) -> None:
        if not self._collected_defaults or self._restore_store is None:
            return
        restore_button = RestoreDefaultsButton(self._collected_defaults, self._restore_store, self)
        self.headerLayout.replaceWidget(self._restore_slot, restore_button)
        self._restore_slot.deleteLater()

    def add_row(self, widget: QWidget) -> None:
        self.body_layout.addWidget(widget)
        if isinstance(widget, RestorableRow):
            self._collected_defaults.append((widget.config_key, widget.default_value))

    def register_restore_defaults(self, defaults: DefaultsMap) -> None:
        self._collected_defaults.extend(defaults)

    def _restore_defaults(self) -> None:
        if self._restore_store is None:
            return
        for key, default in self._collected_defaults:
            self._restore_store.write(key, default)

    def add_header_help(self, explanation: str) -> HelpButton:
        help_button = HelpButton(explanation, self)
        self.headerLayout.replaceWidget(self._help_slot, help_button)
        self._help_slot.deleteLater()
        return help_button

    def add_header_button(self, button: QWidget) -> None:
        self.headerLayout.replaceWidget(self._search_slot, button)
        self._search_slot.deleteLater()
