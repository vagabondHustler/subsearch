from PySide6.QtCore import QSize, QTimer
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget
from qfluentwidgets import BodyLabel, HeaderCardWidget

from subsearch.ui.state.store import SettingsStore
from subsearch.ui.theme.metrics import ROW_INSET, TOOL_BUTTON_SIZE
from subsearch.ui.theme.separators import make_fading_separator
from subsearch.ui.theme.typography import apply_body_font, apply_title_font
from subsearch.ui.widgets.setting_rows import DefaultsMap, HelpButton, RestoreDefaultsButton

CARD_PANEL_OPACITY = 0.4
CARD_FILL_COLOR = QColor(255, 255, 255, 13)
CARD_BORDER_COLOR = QColor(0, 0, 0, 48)
CARD_BORDER_RADIUS = 6.0


def build_section_header(config_key: str, parent: QWidget) -> QHBoxLayout:
    from subsearch.ui.cards.descriptions import SETTING_DESCRIPTIONS

    description = SETTING_DESCRIPTIONS[config_key]
    title_label = BodyLabel(description.title, parent)
    apply_body_font(title_label)
    help_button = HelpButton(description.explanation, parent)
    header = QHBoxLayout()
    header.setContentsMargins(ROW_INSET, 10, ROW_INSET, 4)
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

        # Reserve fixed slots: stretch → help slot → restore slot.
        # Placeholders keep both positions stable whether or not each button is present.
        self.headerLayout.addStretch(1)
        self._restore_slot = _make_button_placeholder(self)
        self.headerLayout.addWidget(self._restore_slot)
        self._help_slot = _make_button_placeholder(self)
        self.headerLayout.addWidget(self._help_slot)

        if not show_restore_button:
            self._restore_slot.hide()
        elif store is not None:
            QTimer.singleShot(0, self._wire_restore_button)

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
        self.vBoxLayout.insertWidget(index, make_fading_separator())

    def _wire_restore_button(self) -> None:
        if not self._collected_defaults or self._restore_store is None:
            return
        restore_button = RestoreDefaultsButton(self._collected_defaults, self._restore_store, self)
        self.headerLayout.replaceWidget(self._restore_slot, restore_button)
        self._restore_slot.deleteLater()

    def add_row(self, widget: QWidget) -> None:
        self.body_layout.addWidget(widget)
        if hasattr(widget, "config_key") and hasattr(widget, "default_value"):
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
