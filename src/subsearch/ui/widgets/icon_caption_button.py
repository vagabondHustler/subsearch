from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QVBoxLayout, QWidget
from qfluentwidgets import CaptionLabel, TransparentToolButton

from subsearch.ui.theme.metrics import TOOL_BUTTON_SIZE, TOOL_ICON_SIZE
from subsearch.ui.theme.typography import apply_caption_font


class CaptionedToolButton(QWidget):
    def __init__(
        self,
        caption: str,
        button: TransparentToolButton | None = None,
        icon: QIcon | None = None,
        parent: QWidget | None = None,
        button_size: int = TOOL_BUTTON_SIZE,
        icon_size: int = TOOL_ICON_SIZE,
    ) -> None:
        super().__init__(parent)
        self.button = button if button is not None else TransparentToolButton(self)
        self.button.setFixedSize(button_size, button_size)
        self.button.setIconSize(QSize(icon_size, icon_size))
        if icon is not None:
            self.button.setIcon(icon)

        self.caption_label = CaptionLabel(caption, self)
        apply_caption_font(self.caption_label)

        column = QVBoxLayout(self)
        column.setContentsMargins(0, 0, 0, 0)
        column.setSpacing(0)
        column.addWidget(self.button, alignment=Qt.AlignmentFlag.AlignHCenter)
        column.addWidget(self.caption_label, alignment=Qt.AlignmentFlag.AlignHCenter)

    @property
    def clicked(self):
        return self.button.clicked
