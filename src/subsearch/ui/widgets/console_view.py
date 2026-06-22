from PySide6.QtCore import QSize, Qt, QTimer
from PySide6.QtGui import QColor, QFont, QResizeEvent
from PySide6.QtWidgets import QListWidget, QListWidgetItem, QVBoxLayout, QWidget
from qfluentwidgets import BodyLabel

from subsearch.ui.services.console_view import ConsoleViewSink
from subsearch.ui.theme.palette import NEUTRAL_1
from subsearch.ui.theme.typography import BODY_FONT_SIZE, SEMI_BOLD, apply_body_font

CONSOLE_FONT_FAMILY = "Consolas"
CONSOLE_LINE_HEIGHT = BODY_FONT_SIZE + 2
LABEL_TO_LIST_SPACING = 4

# Matches yaspin's "arc" spinner used by the terminal console, so the GUI banner
# animates with the same glyphs the terminal shows.
SPINNER_FRAMES = ("◜", "◠", "◝", "◞", "◡", "◟")
SPINNER_INTERVAL_MS = 100
SPINNER_DONE_MARK = "✔"

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

        # The banner header animates while active; the status row is the single
        # transient line that updates in place beneath it, mirroring the terminal.
        self._banner_item: QListWidgetItem | None = None
        self._banner_title = ""
        self._status_item: QListWidgetItem | None = None
        self._spinner_frame = 0

        self._spinner_timer = QTimer(self)
        self._spinner_timer.setInterval(SPINNER_INTERVAL_MS)
        self._spinner_timer.timeout.connect(self._tick_spinner)

        self._replay_history()
        # Queued so slots run on the GUI thread even when the worker thread emits
        # the signals directly from Logger.write.
        connection = Qt.ConnectionType.QueuedConnection
        sink.line_appended.connect(self._append, connection)
        sink.banner_started.connect(self._start_banner, connection)
        sink.banner_finished.connect(self._finish_banner, connection)
        sink.status_updated.connect(self._update_status, connection)

    def height_for_lines(self, line_count: int) -> int:
        return int(self._label.sizeHint().height()) + LABEL_TO_LIST_SPACING + line_count * CONSOLE_LINE_HEIGHT

    @staticmethod
    def _console_font() -> QFont:
        font = QFont(CONSOLE_FONT_FAMILY)
        font.setPixelSize(BODY_FONT_SIZE)
        font.setWeight(SEMI_BOLD)
        return font

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        self._list.scrollToBottom()

    def _replay_history(self) -> None:
        dispatch = {
            "line": self._append,
            "banner": self._start_banner,
            "finish": self._finish_banner,
            "status": self._update_status,
        }
        for kind, payload in self._sink.history():
            dispatch[kind](payload)

    def _new_item(self, message: str) -> QListWidgetItem:
        item = QListWidgetItem(message)
        item.setForeground(QColor(NEUTRAL_1))
        item.setFont(self._console_font())
        item.setSizeHint(QSize(0, CONSOLE_LINE_HEIGHT))
        return item

    def _append(self, message: str) -> None:
        self._list.addItem(self._new_item(message))
        self._list.scrollToBottom()

    def _start_banner(self, title: str) -> None:
        self._banner_title = title
        self._spinner_frame = 0
        self._banner_item = self._new_item(self._banner_text())
        self._list.addItem(self._banner_item)
        self._list.scrollToBottom()
        self._spinner_timer.start()

    def _update_status(self, message: str) -> None:
        if self._banner_item is None:
            self._append(message)
            return
        if self._status_item is None:
            self._status_item = self._new_item("")
            self._list.addItem(self._status_item)
        self._status_item.setText(f"  {message}")
        self._list.scrollToBottom()

    def _finish_banner(self, done_title: str) -> None:
        if self._banner_item is None:
            return
        self._spinner_timer.stop()
        self._banner_item.setText(f"{SPINNER_DONE_MARK} {done_title}")
        self._banner_item = None
        self._status_item = None
        self._banner_title = ""

    def _tick_spinner(self) -> None:
        if self._banner_item is None:
            return
        self._spinner_frame = (self._spinner_frame + 1) % len(SPINNER_FRAMES)
        self._banner_item.setText(self._banner_text())

    def _banner_text(self) -> str:
        return f"{SPINNER_FRAMES[self._spinner_frame]} {self._banner_title}"
