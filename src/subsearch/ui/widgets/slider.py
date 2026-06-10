from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QColor, QPainter, QPen
from qfluentwidgets import Slider
from qfluentwidgets.components.widgets.slider import SliderHandle

HANDLE_SIZE = 32
HANDLE_CENTER = HANDLE_SIZE // 2
HANDLE_RADIUS = 8
HANDLE_FILL_COLOR = QColor("#c8c8c7")
HANDLE_BORDER_COLOR = QColor("#1c2023")
HANDLE_BORDER_WIDTH = 2
HOVER_DISC_RADIUS = 14
HOVER_DISC_COLOR = QColor(255, 255, 255, 21)
PRESSED_DISC_COLOR = QColor(255, 255, 255, 12)


class CircleDotHandle(SliderHandle):
    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.setFixedSize(HANDLE_SIZE, HANDLE_SIZE)
        self._hovered = False
        self._pressed = False

    def enterEvent(self, e) -> None:
        self._hovered = True
        self.update()

    def leaveEvent(self, e) -> None:
        self._hovered = False
        self.update()

    def mousePressEvent(self, e) -> None:
        self._pressed = True
        self.update()
        self.pressed.emit()
        self._drag_to(e)

    def mouseMoveEvent(self, e) -> None:
        self._drag_to(e)

    def mouseReleaseEvent(self, e) -> None:
        self._pressed = False
        self.update()
        self.released.emit()

    def _drag_to(self, e) -> None:
        self.parent().update_value_from_handle(e.position().toPoint())

    def paintEvent(self, e) -> None:
        center = QPoint(HANDLE_CENTER, HANDLE_CENTER)
        painter = QPainter(self)
        painter.setRenderHints(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)

        if self._pressed:
            painter.setBrush(PRESSED_DISC_COLOR)
            painter.drawEllipse(center, HOVER_DISC_RADIUS, HOVER_DISC_RADIUS)
        elif self._hovered:
            painter.setBrush(HOVER_DISC_COLOR)
            painter.drawEllipse(center, HOVER_DISC_RADIUS, HOVER_DISC_RADIUS)

        painter.setPen(QPen(HANDLE_BORDER_COLOR, HANDLE_BORDER_WIDTH))
        painter.setBrush(HANDLE_FILL_COLOR)
        painter.drawEllipse(center, HANDLE_RADIUS, HANDLE_RADIUS)


class CircleDotSlider(Slider):
    def _postInit(self) -> None:
        super()._postInit()
        self.handle.deleteLater()
        self.handle = CircleDotHandle(self)
        self.handle.pressed.connect(self.sliderPressed)
        self.handle.released.connect(self.sliderReleased)
        self.handle.setHandleColor(self.lightGrooveColor, self.darkGrooveColor)
        self.setMinimumHeight(HANDLE_SIZE)
        self._adjustHandlePos()

    def update_value_from_handle(self, handle_position: QPoint) -> None:
        self.setValue(self._posToValue(self.handle.mapToParent(handle_position)))
