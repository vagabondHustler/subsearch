from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget

from subsearch.ui.icons.lucide import LucideIcon
from subsearch.ui.theme.metrics import IN_FIELD_BUTTON_SIZE
from subsearch.ui.theme.typography import TEXT_COLOR
from subsearch.ui.widgets.icon_button_line_edit import IconButtonLineEdit
from subsearch.ui.widgets.ripple_spinner import RippleSpinner


class SearchLineEdit(IconButtonLineEdit):
    def __init__(
        self,
        placeholder: str = "",
        icon: LucideIcon = LucideIcon.SEARCH,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(placeholder, icon, parent)
        self._spinner = RippleSpinner(TEXT_COLOR, self._button)
        self._spinner.setFixedSize(IN_FIELD_BUTTON_SIZE, IN_FIELD_BUTTON_SIZE)
        self._spinner.move(0, 0)

    def start_spinner(self) -> None:
        self._button.setIcon(QIcon())
        self._spinner.start()

    def stop_spinner(self) -> None:
        self._spinner.stop()
        self._button.setIcon(self._icon)
