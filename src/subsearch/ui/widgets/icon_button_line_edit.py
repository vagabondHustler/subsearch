from typing import cast

from PySide6.QtCore import QSize, SignalInstance
from PySide6.QtWidgets import QWidget
from qfluentwidgets import LineEdit, TransparentToolButton

from subsearch.ui.compat.qfluent import embed_trailing_widget, flatten_line_edit
from subsearch.ui.icons.lucide import LucideIcon, lucide_qicon
from subsearch.ui.theme.metrics import IN_FIELD_BUTTON_SIZE, SMALL_ICON_SIZE
from subsearch.ui.theme.typography import TEXT_COLOR, apply_body_font


class IconButtonLineEdit(LineEdit):
    def __init__(
        self,
        placeholder: str = "",
        icon: LucideIcon = LucideIcon.SEARCH,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._icon = lucide_qicon(icon, TEXT_COLOR)
        self.setPlaceholderText(placeholder)
        apply_body_font(self)
        flatten_line_edit(self)

        self._button = TransparentToolButton(self)
        self._button.setIcon(self._icon)
        self._button.setFixedSize(IN_FIELD_BUTTON_SIZE, IN_FIELD_BUTTON_SIZE)
        self._button.setIconSize(QSize(SMALL_ICON_SIZE, SMALL_ICON_SIZE))
        embed_trailing_widget(self, self._button, IN_FIELD_BUTTON_SIZE)

    @property
    def button_clicked(self) -> SignalInstance:
        return cast(SignalInstance, self._button.clicked)

    def set_button_enabled(self, enabled: bool) -> None:
        self._button.setEnabled(enabled)

    def set_button_tooltip(self, tooltip: str) -> None:
        self._button.setToolTip(tooltip)
