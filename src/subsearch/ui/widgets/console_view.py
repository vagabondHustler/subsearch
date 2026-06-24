from PySide6.QtCore import QSize, Qt, QTimer
from PySide6.QtGui import QColor, QFont, QResizeEvent
from PySide6.QtWidgets import QListWidget, QListWidgetItem, QVBoxLayout, QWidget
from qfluentwidgets import BodyLabel

from subsearch.runtime.recorder import ConsoleGroup, ConsoleSnapshot, ConsoleTheme
from subsearch.ui.services.console_view import ConsoleViewSink
from subsearch.ui.theme.typography import BODY_FONT_SIZE, SEMI_BOLD, apply_body_font

CONSOLE_FONT_FAMILY = "Consolas"
CONSOLE_LINE_HEIGHT = BODY_FONT_SIZE + 2
LABEL_TO_LIST_SPACING = 4

# rich "dots" spinner the terminal console draws, one frame per name
SPINNER_FRAMES = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
SPINNER_INTERVAL_MS = 100

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


def _color_from_style(style: str) -> QColor:
    # rich style strings carry optional modifiers (e.g. "bold #f38ba8"); the UI only needs the color token.
    for token in style.split():
        if token.startswith("#") or token not in {"bold", "italic", "dim", "normal"}:
            color = QColor(token)
            if color.isValid():
                return color
    return QColor()


class ConsoleView(QWidget):
    def __init__(self, sink: ConsoleViewSink, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._sink = sink
        self._theme = ConsoleTheme()  # the same default the terminal console renders, so both stay 1:1
        self._active_item: QListWidgetItem | None = None
        self._active_title = ""
        self._spinner_frame = 0

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

        latest = sink.latest()
        if latest is not None:
            self._render(latest)

        # Queued so the slot runs on the GUI thread even when the recorder drain
        # thread emits the signal directly.
        sink.snapshot_received.connect(self._render, Qt.ConnectionType.QueuedConnection)

        self._spinner_timer = QTimer(self)
        self._spinner_timer.setInterval(SPINNER_INTERVAL_MS)
        self._spinner_timer.timeout.connect(self._advance_spinner)
        self._spinner_timer.start()

    def height_for_lines(self, line_count: int) -> int:
        label_height: int = self._label.sizeHint().height()
        return label_height + LABEL_TO_LIST_SPACING + line_count * CONSOLE_LINE_HEIGHT

    @staticmethod
    def _console_font() -> QFont:
        font = QFont(CONSOLE_FONT_FAMILY)
        font.setPixelSize(BODY_FONT_SIZE)
        font.setWeight(SEMI_BOLD)
        return font

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        self._list.scrollToBottom()

    def _render(self, snapshot: ConsoleSnapshot) -> None:
        self._list.clear()
        self._active_item = None
        if snapshot.summary_pinned_at_top:
            for summary in snapshot.pinned_summaries:
                self._append(summary.text, _color_from_style(summary.color))
        for group in snapshot.groups:
            self._render_group(group, snapshot)
        self._list.scrollToBottom()

    def _render_group(self, group: ConsoleGroup, snapshot: ConsoleSnapshot) -> None:
        if group.active:
            self._active_item = self._append(group.title, _color_from_style(self._theme.active_title_style))
            self._active_title = group.title
            self._paint_spinner()
            for line in group.transient_lines:
                self._append(line.text, _color_from_style(line.color))
        else:
            self._append(f"{snapshot.done_marker} {group.title}", _color_from_style(group.marker_color))
        if not snapshot.summary_pinned_at_top and group.summary is not None:
            self._append(group.summary, _color_from_style(group.marker_color))

    def _advance_spinner(self) -> None:
        if self._active_item is None:
            return
        self._spinner_frame = (self._spinner_frame + 1) % len(SPINNER_FRAMES)
        self._paint_spinner()

    def _paint_spinner(self) -> None:
        if self._active_item is not None:
            self._active_item.setText(f"{SPINNER_FRAMES[self._spinner_frame]} {self._active_title}")

    def _append(self, message: str, color: QColor) -> QListWidgetItem:
        item = QListWidgetItem(message)
        item.setForeground(color)
        item.setFont(self._console_font())
        item.setSizeHint(QSize(0, CONSOLE_LINE_HEIGHT))
        self._list.addItem(item)
        return item
