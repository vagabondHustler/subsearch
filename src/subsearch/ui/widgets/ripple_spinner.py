from PySide6.QtCore import QRectF, Qt, QTimer
from PySide6.QtGui import QColor, QPainter, QPaintEvent, QPen, QPixmap
from PySide6.QtWidgets import QWidget

from subsearch.ui.theme.typography import TEXT_COLOR

FRAME_INTERVAL_MS = 16
CYCLE_MS = 2000
_RING_PHASE_OFFSET = 0.5
_RING_WIDTH = 2
_RING_COUNT = 2


def paint_ripple(painter: QPainter, width: float, height: float, color: QColor, progress: float) -> None:
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    center_x = width / 2
    center_y = height / 2
    max_radius = min(width, height) / 2 - _RING_WIDTH
    for ring in range(_RING_COUNT):
        phase = (progress + ring * _RING_PHASE_OFFSET) % 1.0
        radius = phase * max_radius
        ring_color = QColor(color)
        ring_color.setAlphaF(1.0 - phase)
        painter.setPen(QPen(ring_color, _RING_WIDTH))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(QRectF(center_x - radius, center_y - radius, radius * 2, radius * 2))


def ripple_pixmap(size: int, color: str, progress: float) -> QPixmap:
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    paint_ripple(painter, size, size, QColor(color), progress)
    painter.end()
    return pixmap


class RippleSpinner(QWidget):
    def __init__(self, color: str = TEXT_COLOR, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self._color = QColor(color)
        self._progress = 0.0
        self._timer = QTimer(self)
        self._timer.setInterval(FRAME_INTERVAL_MS)
        self._timer.timeout.connect(self._advance)
        self.hide()

    def start(self) -> None:
        if self._timer.isActive():
            return
        self._progress = 0.0
        self.show()
        self.raise_()
        self._timer.start()

    def stop(self) -> None:
        self._timer.stop()
        self.hide()

    def is_running(self) -> bool:
        return self._timer.isActive()

    def _advance(self) -> None:
        self._progress = (self._progress + FRAME_INTERVAL_MS / CYCLE_MS) % 1.0
        self.update()

    def paintEvent(self, _event: QPaintEvent) -> None:
        painter = QPainter(self)
        paint_ripple(painter, self.width(), self.height(), self._color, self._progress)
        painter.end()
