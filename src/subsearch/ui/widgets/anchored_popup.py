from PySide6.QtCore import QPoint, QRect, Qt
from PySide6.QtGui import QShowEvent
from PySide6.QtWidgets import QApplication, QFrame, QWidget

from subsearch.ui.compat.qfluent import apply_popup_acrylic
from subsearch.ui.theme import palette

POPUP_GAP = 6


class AnchoredPopup(QFrame):
    def __init__(self, anchor: QWidget, window_flags: Qt.WindowType, acrylic: bool = False) -> None:
        super().__init__(anchor.window())
        self._anchor = anchor
        self._acrylic = acrylic
        self.setWindowFlags(window_flags | Qt.WindowType.FramelessWindowHint)
        if acrylic:
            # Must be set before the native window is created; toggling it later
            # breaks background erasing and repaints smear over each other.
            self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setObjectName("anchoredPopup")
        self._apply_background("transparent" if acrylic else palette.POPUP_BACKGROUND)

    def _apply_background(self, background: str) -> None:
        self.setStyleSheet(
            f"#anchoredPopup {{"
            f" background-color: {background};"
            f" border: 1px solid {palette.POPUP_BORDER};"
            f" border-radius: 6px;"
            f" }}"
        )

    def showEvent(self, event: QShowEvent) -> None:
        # Reapplied on every show: hiding a popup can recreate its native window,
        # and the compositor effect is bound to the old window handle.
        if self._acrylic:
            if not apply_popup_acrylic(self):
                self._acrylic = False
                self._apply_background(palette.POPUP_BACKGROUND)
        super().showEvent(event)

    def anchor_rect_contains(self, global_position: QPoint) -> bool:
        anchor_top_left = self._anchor.mapToGlobal(QPoint(0, 0))
        return self._anchor.rect().translated(anchor_top_left).contains(global_position)

    def show_above(self) -> None:
        self.adjustSize()
        anchor_top_left = self._anchor.mapToGlobal(QPoint(0, 0))
        anchor_center_x = anchor_top_left.x() + self._anchor.width() // 2
        anchor_bottom = anchor_top_left.y() + self._anchor.height()

        screen_area = self._screen_area(anchor_top_left)
        if screen_area is None:
            return

        x = anchor_center_x - self.width() // 2
        x = max(screen_area.left(), min(x, screen_area.right() - self.width() + 1))

        y = anchor_top_left.y() - self.height() - POPUP_GAP
        if y < screen_area.top():
            y = anchor_bottom + POPUP_GAP
        y = max(screen_area.top(), min(y, screen_area.bottom() - self.height() + 1))

        self.move(QPoint(x, y))
        self.show()
        self.raise_()

    def show_below(self, centered: bool = False) -> None:
        self.reposition_below(centered)
        self.show()
        self.raise_()

    def reposition_below(self, centered: bool = False) -> None:
        self.adjustSize()
        anchor_top_left = self._anchor.mapToGlobal(QPoint(0, 0))
        anchor_bottom = anchor_top_left.y() + self._anchor.height()

        screen_area = self._screen_area(anchor_top_left)
        if screen_area is None:
            return

        if centered:
            anchor_center_x = anchor_top_left.x() + self._anchor.width() // 2
            preferred_x = anchor_center_x - self.width() // 2
        else:
            preferred_x = anchor_top_left.x()
        x = max(screen_area.left(), min(preferred_x, screen_area.right() - self.width() + 1))

        y = anchor_bottom + POPUP_GAP
        if y + self.height() > screen_area.bottom():
            y = anchor_top_left.y() - self.height() - POPUP_GAP
        y = max(screen_area.top(), min(y, screen_area.bottom() - self.height() + 1))

        self.move(QPoint(x, y))

    def _screen_area(self, anchor_top_left: QPoint) -> QRect | None:
        screen = self.screen() or QApplication.screenAt(anchor_top_left)
        if screen is None:
            return None
        return screen.availableGeometry()
