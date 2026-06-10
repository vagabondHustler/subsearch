from PySide6.QtCore import QPoint, Qt, QTimer
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import QApplication, QFrame, QTextBrowser, QVBoxLayout, QWidget

from subsearch.ui.theme.typography import CAPTION_FONT_SIZE, TEXT_COLOR, body_font

POPUP_GAP = 6
POPUP_MIN_WIDTH = 580
POPUP_MAX_WIDTH = 1100
POPUP_MAX_HEIGHT = 420
CONTENT_MARGIN = 20
HIDE_GRACE_MS = 300


class MarkdownPopup(QFrame):
    def __init__(self, anchor: QWidget) -> None:
        super().__init__(anchor.window())
        self._anchor = anchor

        self.setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)
        self.setMouseTracking(True)
        self.setObjectName("markdownPopup")
        self.setStyleSheet(
            "#markdownPopup {" " background-color: #2b2b2b;" " border: 1px solid #454545;" " border-radius: 6px;" " }"
        )

        caption_font = body_font()
        caption_font.setPixelSize(CAPTION_FONT_SIZE)

        self._browser = QTextBrowser(self)
        self._browser.setFont(caption_font)
        self._browser.setOpenExternalLinks(True)
        self._browser.setFrameShape(QFrame.Shape.NoFrame)
        self._browser.setLineWrapMode(QTextBrowser.LineWrapMode.NoWrap)
        self._browser.setMaximumHeight(POPUP_MAX_HEIGHT)
        self._browser.setStyleSheet(f"QTextBrowser {{ background: transparent; color: {TEXT_COLOR}; }}")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.addWidget(self._browser)

        self._hide_timer = QTimer(self)
        self._hide_timer.setSingleShot(True)
        self._hide_timer.setInterval(HIDE_GRACE_MS)
        self._hide_timer.timeout.connect(self.hide)

    def set_markdown(self, markdown: str) -> None:
        self._browser.setMarkdown(markdown)
        self._fit_width_to_content()

    def _fit_width_to_content(self) -> None:
        self._browser.document().adjustSize()
        content_width = int(self._browser.document().idealWidth()) + CONTENT_MARGIN
        width = max(POPUP_MIN_WIDTH, min(content_width, POPUP_MAX_WIDTH))
        self._browser.setFixedWidth(width)

    def show_above(self) -> None:
        self.adjustSize()
        anchor_top_left = self._anchor.mapToGlobal(QPoint(0, 0))
        anchor_center_x = anchor_top_left.x() + self._anchor.width() // 2
        anchor_bottom = anchor_top_left.y() + self._anchor.height()

        screen = self.screen() or QApplication.screenAt(anchor_top_left)
        screen_area = screen.availableGeometry()

        x = anchor_center_x - self.width() // 2
        x = max(screen_area.left(), min(x, screen_area.right() - self.width() + 1))

        y = anchor_top_left.y() - self.height() - POPUP_GAP
        if y < screen_area.top():
            y = anchor_bottom + POPUP_GAP
        y = max(screen_area.top(), min(y, screen_area.bottom() - self.height() + 1))

        self.move(QPoint(x, y))
        self.show()
        self.raise_()
        self._update_hide_timer()

    def _cursor_over_popup_or_button(self) -> bool:
        cursor_position = QCursor.pos()
        if self.geometry().contains(cursor_position):
            return True
        button_top_left = self._anchor.mapToGlobal(QPoint(0, 0))
        return self._anchor.rect().translated(button_top_left).contains(cursor_position)

    def _update_hide_timer(self) -> None:
        if self._cursor_over_popup_or_button():
            self._hide_timer.stop()
        elif not self._hide_timer.isActive():
            self._hide_timer.start()

    def mouseMoveEvent(self, event) -> None:
        self._update_hide_timer()
        super().mouseMoveEvent(event)
