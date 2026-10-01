from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QCursor, QMouseEvent, QTextOption
from PySide6.QtWidgets import QFrame, QTextBrowser, QVBoxLayout, QWidget

from subsearch.ui.theme import palette
from subsearch.ui.theme.typography import POPUP_FONT_SIZE, TEXT_COLOR, body_font
from subsearch.ui.widgets.anchored_popup import AnchoredPopup

POPUP_MIN_WIDTH = 580
POPUP_MAX_WIDTH = 1100
POPUP_MAX_HEIGHT = 420
CONTENT_MARGIN = 20
CONTENT_HEIGHT_MARGIN = 4
HIDE_GRACE_MS = 300


class MarkdownPopup(AnchoredPopup):
    def __init__(self, anchor: QWidget) -> None:
        super().__init__(anchor, Qt.WindowType.Popup)
        self.setMouseTracking(True)

        caption_font = body_font()
        caption_font.setPixelSize(POPUP_FONT_SIZE)

        self._browser = QTextBrowser(self)
        self._browser.setFont(caption_font)
        self._browser.setOpenExternalLinks(True)
        self._browser.setFrameShape(QFrame.Shape.NoFrame)
        self._browser.setLineWrapMode(QTextBrowser.LineWrapMode.WidgetWidth)
        self._browser.setWordWrapMode(QTextOption.WrapMode.WrapAtWordBoundaryOrAnywhere)
        self._browser.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._browser.setStyleSheet(
            f"QTextBrowser {{ background: transparent; color: {TEXT_COLOR}; }}"
            "QScrollBar:vertical {"
            " background: transparent;"
            " width: 8px;"
            " margin: 4px 2px 4px 0;"
            "}"
            "QScrollBar::handle:vertical {"
            f" background: {palette.NEUTRAL_4};"
            " min-height: 24px;"
            " border-radius: 4px;"
            "}"
            "QScrollBar::handle:vertical:hover {"
            f" background: {palette.NEUTRAL_3};"
            "}"
            "QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }"
            "QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: transparent; }"
        )

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
        self._browser.document().setTextWidth(self._browser.viewport().width())
        content_height = int(self._browser.document().size().height()) + CONTENT_HEIGHT_MARGIN
        self._browser.setFixedHeight(min(content_height, POPUP_MAX_HEIGHT))

    def show_above(self) -> None:
        super().show_above()
        self._update_hide_timer()

    def _cursor_over_popup_or_button(self) -> bool:
        cursor_position = QCursor.pos()
        if self.geometry().contains(cursor_position):
            return True
        return self.anchor_rect_contains(cursor_position)

    def _update_hide_timer(self) -> None:
        if self._cursor_over_popup_or_button():
            self._hide_timer.stop()
        elif not self._hide_timer.isActive():
            self._hide_timer.start()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        self._update_hide_timer()
        super().mouseMoveEvent(event)
