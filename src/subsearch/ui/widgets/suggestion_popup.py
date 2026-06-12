from PySide6.QtCore import QEvent, QObject, Qt, Signal
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from subsearch.parsing.imdb_lookup import TitleSuggestion
from subsearch.ui.theme import palette
from subsearch.ui.theme.typography import (
    TEXT_COLOR,
    apply_body_font,
    apply_caption_font,
)
from subsearch.ui.widgets.anchored_popup import AnchoredPopup

ROW_PADDING = "4px 10px"
ACCEPT_KEYS = (Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Tab)
NAVIGATION_HINT = "↑↓ navigate    Enter accept    Esc search as typed"


class SuggestionRow(QLabel):
    clicked = Signal(int)
    hovered = Signal(int)

    def __init__(self, index: int, text: str, parent: QWidget | None = None) -> None:
        super().__init__(text, parent)
        self.index = index
        apply_body_font(self)
        self.setMouseTracking(True)
        self.render_selected(False)

    def render_selected(self, selected: bool) -> None:
        background = palette.NEUTRAL_4 if selected else "transparent"
        self.setStyleSheet(
            f"QLabel {{ color: {TEXT_COLOR}; background-color: {background};"
            f" border-radius: 4px; padding: {ROW_PADDING}; }}"
        )

    def mousePressEvent(self, event) -> None:
        self.clicked.emit(self.index)

    def enterEvent(self, event) -> None:
        self.hovered.emit(self.index)


class TitleSuggestionPopup(AnchoredPopup):
    suggestion_accepted = Signal(object)
    dismissed = Signal()

    def __init__(self, anchor: QWidget) -> None:
        super().__init__(anchor, Qt.WindowType.ToolTip, acrylic=True)
        self._anchor_widget = anchor
        self._suggestions: list[TitleSuggestion] = []
        self._rows: list[SuggestionRow] = []
        self._selected_index = 0

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(6, 6, 6, 6)
        self._layout.setSpacing(2)

        self._hint_label = QLabel(NAVIGATION_HINT, self)
        apply_caption_font(self._hint_label)
        self._hint_label.setStyleSheet(f"color: {palette.NEUTRAL_3}; padding: {ROW_PADDING};")

        anchor.installEventFilter(self)

    def show_suggestions(self, suggestions: list[TitleSuggestion]) -> None:
        self._teardown_rows()
        self._suggestions = suggestions
        self._rows = [
            SuggestionRow(index, suggestion.display_text(), self) for index, suggestion in enumerate(suggestions)
        ]
        for row in self._rows:
            row.clicked.connect(self._accept_index)
            row.hovered.connect(self._select_index)
            self._layout.addWidget(row)
        self._layout.addWidget(self._hint_label)
        self._select_index(0)
        self.setMinimumWidth(self._anchor_widget.width())
        self.show_below()

    def _teardown_rows(self) -> None:
        for row in self._rows:
            self._layout.removeWidget(row)
            row.deleteLater()
        self._layout.removeWidget(self._hint_label)
        self._rows = []

    def _select_index(self, index: int) -> None:
        self._selected_index = index
        for row in self._rows:
            row.render_selected(row.index == index)

    def _accept_index(self, index: int) -> None:
        self.hide()
        self.suggestion_accepted.emit(self._suggestions[index])

    def _dismiss(self) -> None:
        self.hide()
        self.dismissed.emit()

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if not self.isVisible():
            return False
        if event.type() == QEvent.Type.FocusOut:
            self.hide()
            return False
        if event.type() != QEvent.Type.KeyPress or not isinstance(event, QKeyEvent):
            return False
        return self._handle_key(event.key())

    def _handle_key(self, key: int) -> bool:
        if key == Qt.Key.Key_Down:
            self._select_index((self._selected_index + 1) % len(self._rows))
            return True
        if key == Qt.Key.Key_Up:
            self._select_index((self._selected_index - 1) % len(self._rows))
            return True
        if key in ACCEPT_KEYS:
            self._accept_index(self._selected_index)
            return True
        if key == Qt.Key.Key_Escape:
            self._dismiss()
            return True
        return False
