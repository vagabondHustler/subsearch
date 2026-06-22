from collections.abc import Callable
from dataclasses import dataclass

from PySide6.QtCore import QEvent, QPoint, Qt
from PySide6.QtGui import (
    QColor,
    QEnterEvent,
    QKeyEvent,
    QMouseEvent,
    QPainter,
    QPainterPath,
    QPaintEvent,
)
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QLayout,
    QVBoxLayout,
    QWidget,
)

from subsearch.ui.icons.lucide import LucideIcon, lucide_qicon
from subsearch.ui.theme import palette
from subsearch.ui.theme.separators import make_fading_separator
from subsearch.ui.theme.typography import TEXT_COLOR, apply_body_font
from subsearch.ui.widgets.anchored_popup import AnchoredPopup

ROW_PADDING_VERTICAL = 6
ROW_PADDING_HORIZONTAL = 12
ROW_ICON_SIZE = 16
ROW_SPACING = 10
CORNER_RADIUS = 6
ACRYLIC_TINT_ALPHA = 179


@dataclass(frozen=True)
class ContextMenuItem:
    icon: LucideIcon
    label: str
    on_triggered: Callable[[], None]


class ContextMenuRow(QWidget):
    def __init__(self, item: ContextMenuItem, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._item = item
        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(
            ROW_PADDING_HORIZONTAL,
            ROW_PADDING_VERTICAL,
            ROW_PADDING_HORIZONTAL,
            ROW_PADDING_VERTICAL,
        )
        layout.setSpacing(ROW_SPACING)

        icon_label = QLabel(self)
        icon_label.setPixmap(lucide_qicon(item.icon, TEXT_COLOR).pixmap(ROW_ICON_SIZE, ROW_ICON_SIZE))
        icon_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        layout.addWidget(icon_label)

        text_label = QLabel(item.label, self)
        apply_body_font(text_label)
        text_label.setStyleSheet(f"color: {TEXT_COLOR}; background: transparent;")
        text_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        layout.addWidget(text_label)
        layout.addStretch(1)

        self.render_selected(False)

    def render_selected(self, selected: bool) -> None:
        background = palette.NEUTRAL_4 if selected else "transparent"
        self.setStyleSheet(f"ContextMenuRow {{ background-color: {background}; border-radius: 4px; }}")

    def enterEvent(self, event: QEnterEvent) -> None:
        self.render_selected(True)

    def leaveEvent(self, event: QEvent) -> None:
        self.render_selected(False)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        self._item.on_triggered()


class ContextMenuPopup(AnchoredPopup):
    def __init__(self, window: QWidget, items: list[ContextMenuItem]) -> None:
        super().__init__(window, Qt.WindowType.Popup, acrylic=True)
        self._rows: list[ContextMenuRow] = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(0)
        layout.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)
        for index, item in enumerate(items):
            self._add_index_seperator(index, layout)
            row = ContextMenuRow(self._wrap(item), self)
            layout.addWidget(row)
            self._rows.append(row)

    def _add_index_seperator(self, index: int, layout: QVBoxLayout) -> None:
        if index == 0:
            return
        layout.addWidget(make_fading_separator(opacity=0.55, width_fraction=0.9, inset=0))

    def _wrap(self, item: ContextMenuItem) -> ContextMenuItem:
        def triggered() -> None:
            self.hide()
            item.on_triggered()

        return ContextMenuItem(item.icon, item.label, triggered)

    def show_above_point(self, global_point: QPoint) -> None:
        self.adjustSize()
        screen = QApplication.screenAt(global_point) or self.screen()
        area = screen.availableGeometry() if screen else None

        x = global_point.x()
        y = global_point.y() - self.height()
        if area is not None:
            x = max(area.left(), min(x, area.right() - self.width() + 1))
            y = max(area.top(), min(y, area.bottom() - self.height() + 1))

        self.move(QPoint(x, y))
        self.show()
        self.raise_()
        self.activateWindow()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_Escape:
            self.hide()
            return
        super().keyPressEvent(event)

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect().adjusted(0, 0, -1, -1)
        path = QPainterPath()
        path.addRoundedRect(rect, CORNER_RADIUS, CORNER_RADIUS)

        tint = QColor(palette.POPUP_BACKGROUND)
        tint.setAlpha(ACRYLIC_TINT_ALPHA)
        painter.fillPath(path, tint)
        painter.setPen(QColor(palette.POPUP_BORDER))
        painter.drawPath(path)
