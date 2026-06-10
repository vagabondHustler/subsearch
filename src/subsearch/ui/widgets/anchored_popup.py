from PySide6.QtCore import QPoint, Qt
from PySide6.QtWidgets import QApplication, QFrame, QWidget

from subsearch.ui.theme import palette

POPUP_GAP = 6


class AnchoredPopup(QFrame):
    def __init__(self, anchor: QWidget, window_flags: Qt.WindowType) -> None:
        super().__init__(anchor.window())
        self._anchor = anchor
        self.setWindowFlags(window_flags | Qt.WindowType.FramelessWindowHint)
        self.setObjectName("anchoredPopup")
        self.setStyleSheet(
            f"#anchoredPopup {{"
            f" background-color: {palette.POPUP_BACKGROUND};"
            f" border: 1px solid {palette.POPUP_BORDER};"
            f" border-radius: 6px;"
            f" }}"
        )

    def anchor_rect_contains(self, global_position: QPoint) -> bool:
        anchor_top_left = self._anchor.mapToGlobal(QPoint(0, 0))
        return self._anchor.rect().translated(anchor_top_left).contains(global_position)

    def show_above(self) -> None:
        self.adjustSize()
        anchor_top_left = self._anchor.mapToGlobal(QPoint(0, 0))
        anchor_center_x = anchor_top_left.x() + self._anchor.width() // 2
        anchor_bottom = anchor_top_left.y() + self._anchor.height()

        screen = self.screen() or QApplication.screenAt(anchor_top_left)
        if screen is None:
            return
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
