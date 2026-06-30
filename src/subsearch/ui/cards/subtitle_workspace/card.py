from PySide6.QtCore import QSize, Signal
from PySide6.QtGui import QResizeEvent
from PySide6.QtWidgets import QWidget
from qfluentwidgets import LineEdit, TransparentToolButton

from subsearch.ui.cards.base import SettingsCard
from subsearch.ui.cards.descriptions import SETTING_DESCRIPTIONS, CardKey
from subsearch.ui.cards.subtitle_workspace._constants import (
    CARD_BODY_MARGINS,
    FILTER_BAR_WIDTH,
    SEARCH_BAR_WIDTH_FRACTION,
)
from subsearch.ui.compat.qfluent import flatten_line_edit
from subsearch.ui.icons.lucide import LucideIcon, lucide_qicon
from subsearch.ui.theme import palette
from subsearch.ui.theme.metrics import ROW_INSET, SMALL_ICON_SIZE, TOOL_BUTTON_SIZE
from subsearch.ui.theme.separators import SEPARATOR_INSET
from subsearch.ui.theme.typography import apply_body_font


class SubtitleCard(SettingsCard):
    search_text_changed = Signal(str)
    search_confirmed = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        description = SETTING_DESCRIPTIONS[CardKey.AVAILABLE_SUBTITLES]
        super().__init__(description.title, parent=parent)
        self.add_header_help(description.explanation)
        self.viewLayout.setContentsMargins(*CARD_BODY_MARGINS)
        self._add_dead_chevron()
        self._search_bar = self._build_search_bar()
        self.add_header_button(self._search_bar)

    def _add_dead_chevron(self) -> None:
        # Purely decorative: the other cards carry a collapse chevron, so this card
        # shows the same expanded-state chevron for header consistency. It is disabled
        # and wired to nothing, so the card cannot collapse.
        chevron = TransparentToolButton(self)
        chevron.setFixedSize(TOOL_BUTTON_SIZE, TOOL_BUTTON_SIZE)
        chevron.setIconSize(QSize(SMALL_ICON_SIZE, SMALL_ICON_SIZE))
        chevron.setIcon(lucide_qicon(LucideIcon.CHEVRON_DOWN, palette.NEUTRAL_3))
        chevron.setEnabled(False)
        self.headerLayout.insertWidget(0, chevron)

    def _build_search_bar(self) -> LineEdit:
        bar = LineEdit(self)
        bar.setPlaceholderText("Filter subtitles…")
        apply_body_font(bar)
        flatten_line_edit(bar)
        bar.setFixedWidth(FILTER_BAR_WIDTH)
        bar.setClearButtonEnabled(True)
        bar.textChanged.connect(self.search_text_changed)
        bar.returnPressed.connect(self.search_confirmed)
        return bar

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        self._align_filter_bar_to_search_bar()

    def _align_filter_bar_to_search_bar(self) -> None:
        field_area_width = self.width() - 2 * SEPARATOR_INSET
        search_bar_right_inset = SEPARATOR_INSET + round((1 - SEARCH_BAR_WIDTH_FRACTION) / 2 * field_area_width)
        trailing_width = self._header_trailing_width()
        left, top, _, bottom = self.headerLayout.getContentsMargins()
        right_margin = max(ROW_INSET, search_bar_right_inset - trailing_width)
        self.headerLayout.setContentsMargins(left, top, right_margin, bottom)

    def _header_trailing_width(self) -> int:
        spacing = max(self.headerLayout.spacing(), 0)
        filter_index = self._filter_bar_index()
        if filter_index is None:
            return 0
        trailing = 0
        for index in range(filter_index + 1, self.headerLayout.count()):
            widget = self.headerLayout.itemAt(index).widget()
            if widget is not None and widget.isVisible():
                trailing += widget.width() + spacing
        return trailing

    def _filter_bar_index(self) -> int | None:
        for index in range(self.headerLayout.count()):
            if self.headerLayout.itemAt(index).widget() is self._search_bar:
                return index
        return None
