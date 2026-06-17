from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import QListWidget, QListWidgetItem, QVBoxLayout, QWidget
from qfluentwidgets import BodyLabel

from subsearch.ui.services.console_view import ConsoleViewSink
from subsearch.ui.theme.palette import NEUTRAL_1
from subsearch.ui.theme.typography import BODY_FONT_SIZE, SEMI_BOLD, apply_body_font

CONSOLE_FONT_FAMILY = "Consolas"
CONSOLE_LINE_HEIGHT = BODY_FONT_SIZE + 2
LABEL_TO_LIST_SPACING = 4

CONSOLE_STYLE_SHEET = """
QListWidget {
    background: transparent;
    border: none;
    outline: none;
}
QListWidget::item {
    background: transparent;
    border: none;
    padding: 0px 4px;
}
"""


class ConsoleView(QWidget):
    def __init__(self, sink: ConsoleViewSink, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._sink = sink

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(LABEL_TO_LIST_SPACING)

        self._label = BodyLabel("Console", self)
        apply_body_font(self._label)
        layout.addWidget(self._label)

        self._list = QListWidget(self)
        self._list.setStyleSheet(CONSOLE_STYLE_SHEET)
        self._list.setFont(self._console_font())
        self._list.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self._list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._list.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        layout.addWidget(self._list)

        for message in sink.buffer():
            self._append(message)

        # Queued so the slot runs on the GUI thread even when the worker thread
        # emits the signal directly from Logger.write.
        sink.message_received.connect(self._append, Qt.ConnectionType.QueuedConnection)

    def height_for_lines(self, line_count: int) -> int:
        return self._label.sizeHint().height() + LABEL_TO_LIST_SPACING + line_count * CONSOLE_LINE_HEIGHT

    @staticmethod
    def _console_font() -> QFont:
        font = QFont(CONSOLE_FONT_FAMILY)
        font.setPixelSize(BODY_FONT_SIZE)
        font.setWeight(SEMI_BOLD)
        return font

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._list.scrollToBottom()

    def _append(self, message: str) -> None:
        item = QListWidgetItem(message)
        item.setForeground(QColor(NEUTRAL_1))
        item.setFont(self._console_font())
        item.setSizeHint(QSize(0, CONSOLE_LINE_HEIGHT))
        self._list.addItem(item)
        self._list.scrollToBottom()
