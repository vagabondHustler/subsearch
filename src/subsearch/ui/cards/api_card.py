import webbrowser

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QKeyEvent, QKeySequence
from PySide6.QtWidgets import QApplication, QHBoxLayout, QVBoxLayout, QWidget
from qfluentwidgets import BodyLabel, CaptionLabel, LineEdit, TransparentToolButton

from subsearch.parsing import release_parser
from subsearch.runtime.keys import CardKey, ConfigKey
from subsearch.ui.cards.base import SettingsCard
from subsearch.ui.cards.descriptions import SETTING_DESCRIPTIONS
from subsearch.ui.compat.qfluent import embed_trailing_widget, flatten_line_edit
from subsearch.ui.icons.lucide import LucideIcon, lucide_qicon
from subsearch.ui.state.store import SettingsStore
from subsearch.ui.theme.metrics import (
    CARD_CONTENT_INSET,
    IN_FIELD_BUTTON_SIZE,
    ROW_INSET,
    SMALL_ICON_SIZE,
)
from subsearch.ui.theme.typography import (
    TEXT_COLOR,
    apply_body_font,
    apply_caption_font,
    set_error_text,
)
from subsearch.ui.widgets.icon_caption_button import CaptionedToolButton
from subsearch.ui.widgets.setting_rows import TrailingButtonArea

VISIBLE_PREFIX_LENGTH = 4
MASK_CHARACTER = "•"
LINK_BUTTON_ICON_SIZE = 24
LINK_BUTTON_SIZE = 32
LINK_BUTTON_SPACING = 48
API_KEY_CONFIG_KEY = ConfigKey.CREDENTIALS_SUBSOURCE_API_KEY
API_KEY_CONFIG_KEY_EXISTS = ConfigKey.CREDENTIALS_SUBSOURCE_API_KEY_EXISTS
API_KEY_DESCRIPTION_KEY = CardKey.SUBSOURCE_API_KEY
REQUEST_LIMITS_KEY = CardKey.SUBSOURCE_REQUEST_LIMITS
GETTING_API_KEY_KEY = CardKey.SUBSOURCE_GETTING_API_KEY
PROFILE_URL = "https://subsource.net/dashboard/profile"
API_DOCS_URL = "https://subsource.net/api-docs"


def mask_api_key(api_key: str) -> str:
    if len(api_key) <= VISIBLE_PREFIX_LENGTH:
        return MASK_CHARACTER * len(api_key)
    hidden_length = len(api_key) - VISIBLE_PREFIX_LENGTH
    return api_key[:VISIBLE_PREFIX_LENGTH] + MASK_CHARACTER * hidden_length


class MaskedApiKeyLineEdit(LineEdit):
    api_key_changed = Signal()

    def __init__(self, api_key: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._api_key = api_key
        self._revealed = False
        self.setPlaceholderText("sk_...")
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        self.setCursor(Qt.CursorShape.IBeamCursor)
        self._render()

    @property
    def api_key(self) -> str:
        return self._api_key

    def set_revealed(self, revealed: bool) -> None:
        self._revealed = revealed
        self._render()

    def _render(self) -> None:
        self.blockSignals(True)
        super().setText(self._api_key if self._revealed else mask_api_key(self._api_key))
        self.deselect()
        self.end(False)
        self.blockSignals(False)

    def _set_api_key(self, api_key: str) -> None:
        if api_key == self._api_key:
            return
        self._api_key = api_key
        self._render()
        self.api_key_changed.emit()

    def _edit_range(self) -> tuple[int, int]:
        if self.hasSelectedText():
            start = self.selectionStart()
            return start, start + len(self.selectedText())
        caret = self.cursorPosition()
        return caret, caret

    def _replace_range(self, start: int, end: int, text: str) -> None:
        self._set_api_key(self._api_key[:start] + text + self._api_key[end:])
        self.setCursorPosition(start + len(text))

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.matches(QKeySequence.StandardKey.Paste):
            text = QApplication.clipboard().text()
            if text:
                start, end = self._edit_range()
                self._replace_range(start, end, text)
            return
        if event.matches(QKeySequence.StandardKey.Cut):
            if self._revealed:
                QApplication.clipboard().setText(self._api_key)
                self._set_api_key("")
            return
        if event.matches(QKeySequence.StandardKey.Copy):
            QApplication.clipboard().setText(self._api_key if self._revealed else mask_api_key(self._api_key))
            return
        if event.matches(QKeySequence.StandardKey.SelectAll):
            self.selectAll()
            return
        if event.key() == Qt.Key.Key_Backspace:
            start, end = self._edit_range()
            if start == end and start > 0:
                start -= 1
            self._replace_range(start, end, "")
            return
        if event.key() == Qt.Key.Key_Delete:
            start, end = self._edit_range()
            if start == end and end < len(self._api_key):
                end += 1
            self._replace_range(start, end, "")
            return
        if event.text() and event.text().isprintable():
            start, end = self._edit_range()
            self._replace_range(start, end, event.text())
            return
        super().keyPressEvent(event)

    def mouseDoubleClickEvent(self, event) -> None:
        event.accept()


class ApiKeyField(QWidget):
    def __init__(
        self, config_key: str, config_key_exists: str, store: SettingsStore, parent: QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self.config_key = config_key
        self.config_key_exists = config_key_exists
        self.store = store
        api_key = str(store.read(config_key))

        self.line_edit = MaskedApiKeyLineEdit(api_key, self)
        apply_body_font(self.line_edit)
        flatten_line_edit(self.line_edit)
        self.line_edit.api_key_changed.connect(self._on_api_key_changed)

        self._revealed = False
        self.reveal_button = TransparentToolButton(self.line_edit)
        self.reveal_button.setFixedSize(IN_FIELD_BUTTON_SIZE, IN_FIELD_BUTTON_SIZE)
        self.reveal_button.setIconSize(QSize(SMALL_ICON_SIZE, SMALL_ICON_SIZE))
        self.reveal_button.clicked.connect(self._toggle_revealed)
        self._apply_reveal_icon()
        embed_trailing_widget(self.line_edit, self.reveal_button, IN_FIELD_BUTTON_SIZE)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(CARD_CONTENT_INSET, 4, ROW_INSET, 8)
        layout.setSpacing(8)
        layout.addWidget(self.line_edit, stretch=1)
        layout.addWidget(TrailingButtonArea([], None, self))

        self._apply_validation_state(api_key)

    def _toggle_revealed(self) -> None:
        self._revealed = not self._revealed
        self.line_edit.set_revealed(self._revealed)
        self._apply_reveal_icon()

    def _apply_reveal_icon(self) -> None:
        icon = LucideIcon.EYE_OFF if self._revealed else LucideIcon.EYE
        self.reveal_button.setIcon(lucide_qicon(icon, TEXT_COLOR))

    def _on_api_key_changed(self) -> None:
        api_key = self.line_edit.api_key
        self.store.write(self.config_key, api_key)
        self.store.write(self.config_key_exists, bool(api_key))
        self._apply_validation_state(api_key)

    def _apply_validation_state(self, api_key: str) -> None:
        is_error = bool(api_key) and not release_parser.valid_subsource_api_key(api_key)
        set_error_text(self.line_edit, is_error)


class ApiCard(SettingsCard):
    def __init__(self, store: SettingsStore, parent: QWidget | None = None) -> None:
        super().__init__("Subsource", parent=parent)
        self.add_header_help(SETTING_DESCRIPTIONS[API_KEY_DESCRIPTION_KEY].explanation)

        title_label = BodyLabel("API key", self)
        apply_body_font(title_label)
        title_row = QHBoxLayout()
        title_row.setContentsMargins(CARD_CONTENT_INSET, 6, ROW_INSET, 0)
        title_row.addWidget(title_label)
        self.body_layout.addLayout(title_row)

        self.add_row(ApiKeyField(API_KEY_CONFIG_KEY, API_KEY_CONFIG_KEY_EXISTS, store, self))
        self.body_layout.addWidget(self._build_request_limits())
        self.body_layout.addWidget(self._build_getting_started())

    def _build_request_limits(self) -> QWidget:
        container, _ = self._build_description_block(REQUEST_LIMITS_KEY)
        return container

    def _build_description_block(self, description_key: ConfigKey | CardKey) -> tuple[QWidget, QVBoxLayout]:
        description = SETTING_DESCRIPTIONS[description_key]
        container = QWidget(self)
        layout = QVBoxLayout(container)
        layout.setContentsMargins(CARD_CONTENT_INSET, 4, ROW_INSET, 8)
        layout.setSpacing(6)

        title_label = BodyLabel(description.title, self)
        apply_body_font(title_label)
        layout.addWidget(title_label)

        body_label = CaptionLabel(description.explanation, self)
        apply_caption_font(body_label)
        body_label.setWordWrap(True)
        layout.addWidget(body_label)
        return container, layout

    def _build_getting_started(self) -> QWidget:
        container, layout = self._build_description_block(GETTING_API_KEY_KEY)
        layout.addLayout(self._build_link_buttons())
        return container

    def _build_link_buttons(self) -> QHBoxLayout:
        profile_column = self._build_labelled_link("Open profile", PROFILE_URL)
        docs_column = self._build_labelled_link("API docs", API_DOCS_URL)

        button_row = QHBoxLayout()
        button_row.setContentsMargins(0, 8, 0, 0)
        button_row.setSpacing(LINK_BUTTON_SPACING)
        button_row.addStretch(1)
        button_row.addWidget(profile_column, alignment=Qt.AlignmentFlag.AlignVCenter)
        button_row.addWidget(docs_column, alignment=Qt.AlignmentFlag.AlignVCenter)
        button_row.addStretch(1)
        return button_row

    def _build_labelled_link(self, caption: str, url: str) -> QWidget:
        link_button = CaptionedToolButton(caption, icon=lucide_qicon(LucideIcon.EXTERNAL_LINK, TEXT_COLOR), parent=self)
        link_button.clicked.connect(lambda: webbrowser.open(url))
        return link_button
