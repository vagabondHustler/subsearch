from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import QListWidget, QListWidgetItem, QVBoxLayout, QWidget
from qfluentwidgets import BodyLabel

from subsearch.ui.services.log_panel import LogPanelSink
from subsearch.ui.theme.typography import BODY_FONT_SIZE, SEMI_BOLD, apply_body_font

LOG_FONT_FAMILY = "Consolas"

LOG_STYLE_SHEET = """
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


class LogPanel(QWidget):
    def __init__(self, sink: LogPanelSink, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._sink = sink

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        label = BodyLabel("Log", self)
        apply_body_font(label)
        layout.addWidget(label)

        self._list = QListWidget(self)
        self._list.setStyleSheet(LOG_STYLE_SHEET)
        self._list.setFont(self._log_font())
        self._list.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self._list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._list.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        layout.addWidget(self._list)

        for message, color, bold in sink.buffer():
            self._append(message, color, bold)

        # Queued so the slot always runs on the GUI thread even when the worker
        # thread emits the signal directly from Logger.write.
        sink.message_received.connect(self._append, Qt.ConnectionType.QueuedConnection)

    @staticmethod
    def _log_font() -> QFont:
        font = QFont(LOG_FONT_FAMILY)
        font.setPixelSize(BODY_FONT_SIZE)
        font.setWeight(SEMI_BOLD)
        return font

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._list.scrollToBottom()

    def _append(self, message: str, color: str, bold: bool) -> None:
        item = QListWidgetItem(message)
        item.setForeground(QColor(color))
        font = self._log_font()
        if bold:
            font.setWeight(QFont.Weight.Bold)
        item.setFont(font)
        item.setSizeHint(QSize(0, BODY_FONT_SIZE + 2))
        self._list.addItem(item)
        self._list.scrollToBottom()
