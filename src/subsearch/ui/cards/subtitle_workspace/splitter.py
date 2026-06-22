from PySide6.QtCore import QByteArray, QEvent, QRect, QSize, Qt
from PySide6.QtGui import QColor, QEnterEvent, QPainter, QPaintEvent, QPen
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import QSplitter, QSplitterHandle, QWidget

from subsearch.ui.icons.lucide import LucideIcon
from subsearch.ui.theme import palette
from subsearch.ui.widgets.console_view import ConsoleView

_LOG_DEFAULT_VISIBLE_LINES = 4

_HANDLE_HEIGHT = 20
_HANDLE_LINE_WIDTH_FRACTION = 0.75
_ICON_SIZE = 16


class _SplitterHandle(QSplitterHandle):
    def __init__(self, orientation: Qt.Orientation, parent: QSplitter) -> None:
        super().__init__(orientation, parent)
        self.setCursor(Qt.CursorShape.SizeVerCursor)
        svg_bytes = LucideIcon.GRIP_HORIZONTAL.source().encode()
        self._normal_svg = self._recolor(svg_bytes, palette.POPUP_BORDER)
        self._hover_svg = self._recolor(svg_bytes, palette.NEUTRAL_3)
        self._hovered = False

    @staticmethod
    def _recolor(svg_bytes: bytes, color: str) -> bytes:
        return svg_bytes.replace(b"currentColor", color.encode())

    def sizeHint(self) -> QSize:
        return QSize(0, _HANDLE_HEIGHT)

    def enterEvent(self, _event: QEnterEvent) -> None:
        self._hovered = True
        self.update()

    def leaveEvent(self, _event: QEvent) -> None:
        self._hovered = False
        self.update()

    def paintEvent(self, _event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        line_color = palette.NEUTRAL_3 if self._hovered else palette.POPUP_BORDER
        pen = QPen(QColor(line_color), 1)
        painter.setPen(pen)
        mid_y = self.height() // 2
        line_width = int(self.width() * _HANDLE_LINE_WIDTH_FRACTION)
        line_x = (self.width() - line_width) // 2
        icon_gap = _ICON_SIZE // 2 + 4
        center_x = self.width() // 2
        painter.drawLine(line_x, mid_y, center_x - icon_gap, mid_y)
        painter.drawLine(center_x + icon_gap, mid_y, line_x + line_width, mid_y)

        svg_data = self._hover_svg if self._hovered else self._normal_svg
        renderer = QSvgRenderer(QByteArray(svg_data))
        icon_rect = QRect(
            (self.width() - _ICON_SIZE) // 2,
            (self.height() - _ICON_SIZE) // 2,
            _ICON_SIZE,
            _ICON_SIZE,
        )
        renderer.render(painter, icon_rect)
        painter.end()


class _StyledSplitter(QSplitter):
    def createHandle(self) -> QSplitterHandle:
        return _SplitterHandle(self.orientation(), self)


def _build_splitter(top: QWidget, bottom: ConsoleView) -> QSplitter:
    splitter = _StyledSplitter(Qt.Orientation.Vertical)
    splitter.setChildrenCollapsible(False)
    splitter.addWidget(top)
    splitter.addWidget(bottom)
    top.setMinimumHeight(80)
    default_height = bottom.height_for_lines(_LOG_DEFAULT_VISIBLE_LINES)
    bottom.setMinimumHeight(default_height)
    splitter.setSizes([splitter.sizeHint().height() - default_height, default_height])
    splitter.setStretchFactor(0, 1)
    splitter.setStretchFactor(1, 0)
    return splitter
