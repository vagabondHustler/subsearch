from typing import NamedTuple

from PySide6.QtCore import QElapsedTimer, QEvent, QObject, QSize, Qt, Signal
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)
from qfluentwidgets import LineEdit, SmoothScrollDelegate

from subsearch.ui.compat.qfluent import hide_line_edit_focus_underline
from subsearch.ui.icons.lucide import LucideIcon, lucide_qicon
from subsearch.ui.theme import palette
from subsearch.ui.theme.typography import (
    TEXT_COLOR,
    apply_body_font,
    apply_caption_font,
    apply_token_value_font,
)
from subsearch.ui.widgets.anchored_popup import AnchoredPopup
from subsearch.ui.widgets.suggestion_popup import ROW_PADDING, SuggestionRow

MAX_VISIBLE_RESULTS = 8
ROW_HEIGHT_ESTIMATE = 28
NAVIGATION_HINT = "↑↓ navigate    Enter accept    Esc close"
ACCEPT_KEYS = (Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Tab)
OPEN_KEYS = (Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Space, Qt.Key.Key_Down)
CHEVRON_ICON_SIZE = 14
SELECT_FIXED_WIDTH = 200
SELECT_HEIGHT = 33
REOPEN_GUARD_MS = 200


class MatchRank(NamedTuple):
    tier: int
    label_length: int


NO_MATCH_TIER = 3


def rank_match(terms: list[str], query: str) -> MatchRank:
    query_lower = query.lower()
    best_tier = NO_MATCH_TIER
    for term in terms:
        term_lower = term.lower()
        if term_lower == query_lower:
            best_tier = min(best_tier, 0)
        elif term_lower.startswith(query_lower):
            best_tier = min(best_tier, 1)
        elif query_lower in term_lower:
            best_tier = min(best_tier, 2)
    return MatchRank(best_tier, len(terms[0]))


def matching_labels(search_terms_by_label: dict[str, list[str]], query: str) -> list[str]:
    if not query:
        return list(search_terms_by_label)
    ranked = sorted(
        search_terms_by_label,
        key=lambda label: rank_match(search_terms_by_label[label], query),
    )
    return [label for label in ranked if rank_match(search_terms_by_label[label], query).tier < NO_MATCH_TIER]


class FuzzyFinderPopup(AnchoredPopup):
    label_selected = Signal(str)

    def __init__(self, anchor: QWidget, searchable: bool = True) -> None:
        super().__init__(anchor, Qt.WindowType.Popup, acrylic=True)
        self._anchor_widget = anchor
        self._searchable = searchable
        self._search_terms_by_label: dict[str, list[str]] = {}
        self._visible_labels: list[str] = []
        self._rows: list[SuggestionRow] = []
        self._selected_index = 0
        self._time_since_hidden = QElapsedTimer()

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(6, 6, 6, 6)
        self._layout.setSpacing(2)

        self._search_edit = LineEdit(self)
        apply_body_font(self._search_edit)
        self._search_edit.setPlaceholderText("Type to search")
        self._search_edit.setClearButtonEnabled(False)
        hide_line_edit_focus_underline(self._search_edit)
        self._search_edit.textChanged.connect(self._refilter)
        self._search_edit.installEventFilter(self)
        if searchable:
            self._layout.addWidget(self._search_edit)
        else:
            self._search_edit.hide()
            self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self._rows_container = QWidget(self)
        self._rows_layout = QVBoxLayout(self._rows_container)
        self._rows_layout.setContentsMargins(0, 0, 0, 0)
        self._rows_layout.setSpacing(2)

        self._scroll_area = QScrollArea(self)
        self._scroll_area.setWidget(self._rows_container)
        self._scroll_area.setWidgetResizable(True)
        self._scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self._scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self._scroll_area.setStyleSheet("QScrollArea { background: transparent; } QWidget { background: transparent; }")
        self._scroll_delegate = SmoothScrollDelegate(self._scroll_area)
        self._layout.addWidget(self._scroll_area)

        self._hint_label = QLabel(NAVIGATION_HINT, self)
        apply_caption_font(self._hint_label)
        self._hint_label.setStyleSheet(f"color: {palette.NEUTRAL_3}; padding: {ROW_PADDING};")
        self._layout.addWidget(self._hint_label)

    def set_items(self, labels: list[str], aliases_by_label: dict[str, list[str]] | None = None) -> None:
        aliases_by_label = aliases_by_label or {}
        self._search_terms_by_label = {label: [label, *aliases_by_label.get(label, [])] for label in labels}

    def open(self, current_label: str) -> None:
        self._search_edit.blockSignals(True)
        self._search_edit.clear()
        self._search_edit.blockSignals(False)
        self._rebuild_rows(matching_labels(self._search_terms_by_label, ""), preferred_label=current_label)
        self.setMinimumWidth(self._anchor_widget.width())
        self.show_below(centered=True)
        if self._searchable:
            self._search_edit.setFocus()
        else:
            self.setFocus()

    def _refilter(self, query: str) -> None:
        self._rebuild_rows(matching_labels(self._search_terms_by_label, query))
        if self.isVisible():
            self.show_below(centered=True)

    def _rebuild_rows(self, labels: list[str], preferred_label: str | None = None) -> None:
        self._teardown_rows()
        self._visible_labels = labels
        self._rows = [SuggestionRow(index, label, self._rows_container) for index, label in enumerate(labels)]
        for row in self._rows:
            row.clicked.connect(self._accept_index)
            row.hovered.connect(self._select_index)
            self._rows_layout.addWidget(row)
        self._cap_scroll_height()
        if self._rows:
            preferred_index = (
                self._visible_labels.index(preferred_label) if preferred_label in self._visible_labels else 0
            )
            self._select_index(preferred_index)
        self.adjustSize()

    def _cap_scroll_height(self) -> None:
        self._rows_container.adjustSize()
        content_height = self._rows_container.sizeHint().height()
        visible_count = min(len(self._rows), MAX_VISIBLE_RESULTS)
        capped_height = visible_count * ROW_HEIGHT_ESTIMATE if self._rows else 0
        self._scroll_area.setFixedHeight(min(content_height, capped_height))

    def _teardown_rows(self) -> None:
        for row in self._rows:
            self._rows_layout.removeWidget(row)
            row.hide()
            row.deleteLater()
        self._rows = []
        self._visible_labels = []

    def _select_index(self, index: int) -> None:
        self._selected_index = index
        for row in self._rows:
            row.render_selected(row.index == index)
        if 0 <= index < len(self._rows):
            self._scroll_area.ensureWidgetVisible(self._rows[index])

    def _accept_index(self, index: int) -> None:
        self.hide()
        self.label_selected.emit(self._visible_labels[index])

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if event.type() != QEvent.Type.KeyPress or not isinstance(event, QKeyEvent):
            return False
        return self._handle_key(event.key())

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if not self._handle_key(event.key()):
            super().keyPressEvent(event)

    def _handle_key(self, key: int) -> bool:
        if key == Qt.Key.Key_Escape:
            self.hide()
            return True
        if not self._rows:
            return False
        if key == Qt.Key.Key_Down:
            self._select_index((self._selected_index + 1) % len(self._rows))
            return True
        if key == Qt.Key.Key_Up:
            self._select_index((self._selected_index - 1) % len(self._rows))
            return True
        if key in ACCEPT_KEYS:
            self._accept_index(self._selected_index)
            return True
        return False

    def hideEvent(self, event) -> None:
        self._time_since_hidden.restart()
        super().hideEvent(event)

    def closed_recently(self) -> bool:
        return self._time_since_hidden.isValid() and self._time_since_hidden.elapsed() < REOPEN_GUARD_MS


class FuzzySelect(QFrame):
    currentTextChanged = Signal(str)

    def __init__(self, parent: QWidget | None = None, searchable: bool = True) -> None:
        super().__init__(parent)
        self.setObjectName("fuzzySelect")
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedSize(SELECT_FIXED_WIDTH, SELECT_HEIGHT)
        self.setStyleSheet(
            f"#fuzzySelect {{"
            f" background-color: {palette.SELECT_FIELD_BACKGROUND};"
            f" border: 1px solid {palette.POPUP_BORDER};"
            f" border-radius: 6px;"
            f" }}"
            f"#fuzzySelect:hover, #fuzzySelect:focus {{"
            f" background-color: {palette.SELECT_FIELD_BACKGROUND_HOVER};"
            f" border: 1px solid {palette.NEUTRAL_3};"
            f" }}"
        )

        self._current_label = QLabel("", self)
        apply_token_value_font(self._current_label)

        chevron = QLabel(self)
        chevron.setPixmap(
            lucide_qicon(LucideIcon.CHEVRON_DOWN, TEXT_COLOR).pixmap(QSize(CHEVRON_ICON_SIZE, CHEVRON_ICON_SIZE))
        )

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 8, 0)
        layout.setSpacing(6)
        layout.addWidget(self._current_label, stretch=1)
        layout.addWidget(chevron, alignment=Qt.AlignmentFlag.AlignVCenter)

        self._popup = FuzzyFinderPopup(self, searchable)
        self._popup.label_selected.connect(self.setCurrentText)

    def setItems(self, labels: list[str], aliases_by_label: dict[str, list[str]] | None = None) -> None:
        self._popup.set_items(labels, aliases_by_label)
        if not self._current_label.text() and labels:
            self._current_label.setText(labels[0])

    def currentText(self) -> str:
        return self._current_label.text()

    def setCurrentText(self, label: str) -> None:
        if label == self._current_label.text():
            return
        self._current_label.setText(label)
        self.currentTextChanged.emit(label)

    def open_finder(self) -> None:
        self._popup.open(self.currentText())

    def mousePressEvent(self, event) -> None:
        if self._popup.closed_recently():
            return
        self.open_finder()

    def keyPressEvent(self, event) -> None:
        if event.key() in OPEN_KEYS:
            self.open_finder()
            return
        super().keyPressEvent(event)
