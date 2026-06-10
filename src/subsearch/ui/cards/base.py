from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget
from qfluentwidgets import BodyLabel, HeaderCardWidget

from subsearch.ui.theme.metrics import ROW_INSET
from subsearch.ui.theme.separators import make_fading_separator
from subsearch.ui.theme.typography import apply_body_font, apply_title_font
from subsearch.ui.widgets.setting_rows import HelpButton

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


class SettingsCard(HeaderCardWidget):
    def __init__(  # pyright: ignore[reportIncompatibleVariableOverride]
        self, title: str, parent: QWidget | None = None
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

    def add_row(self, widget: QWidget) -> None:
        self.body_layout.addWidget(widget)

    def add_header_help(self, explanation: str) -> HelpButton:
        self.headerLayout.addStretch(1)
        help_button = HelpButton(explanation, self)
        self.headerLayout.addWidget(help_button)
        return help_button
