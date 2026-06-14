from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QFileDialog, QWidget

from subsearch.ui.icons.lucide import LucideIcon
from subsearch.ui.widgets.icon_button_line_edit import IconButtonLineEdit


class BrowseLineEdit(IconButtonLineEdit):
    path_picked = Signal(str)

    def __init__(
        self,
        placeholder: str = "",
        dialog_title: str = "Select destination directory",
        select_file: bool = False,
        icon: LucideIcon = LucideIcon.FOLDER_OPEN,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(placeholder, icon, parent)
        self._dialog_title = dialog_title
        self._select_file = select_file
        self.button_clicked.connect(self._browse)

    def _browse(self) -> None:
        if self._select_file:
            selected, _filter = QFileDialog.getOpenFileName(self.window(), self._dialog_title, self.text())
        else:
            selected = QFileDialog.getExistingDirectory(self.window(), self._dialog_title, self.text())
        if not selected:
            return
        resolved = str(Path(selected))
        self.setText(resolved)
        self.path_picked.emit(resolved)
