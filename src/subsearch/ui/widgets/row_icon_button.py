from PySide6.QtCore import QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget
from qfluentwidgets import TransparentToolButton

from subsearch.ui.theme.metrics import SMALL_ICON_SIZE


class RowIconButton(TransparentToolButton):
    """A transparent icon button sized to a list-item row: the square hover
    highlight fills the full row height while the icon stays centered, so the
    button reads as part of the line rather than a separate control."""

    def __init__(self, icon: QIcon, row_height: int, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setIcon(icon)
        self.setFixedSize(row_height, row_height)
        self.setIconSize(QSize(SMALL_ICON_SIZE, SMALL_ICON_SIZE))
