from pathlib import Path
from typing import Any

from PySide6.QtCore import QSize, Qt, QTimer, Signal
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)
from qfluentwidgets import (
    BodyLabel,
    LineEdit,
    SwitchButton,
    TransparentToolButton,
)

from subsearch.parsing import release_parser
from subsearch.runtime.config.constants import DEFAULT_CONFIG
from subsearch.ui.cards.descriptions import SETTING_DESCRIPTIONS
from subsearch.ui.compat.qfluent import (
    flatten_line_edit,
    thicken_unchecked_switch_border,
)
from subsearch.ui.icons.lucide import LucideIcon, lucide_qicon
from subsearch.ui.state.store import SettingsStore
from subsearch.ui.theme import palette
from subsearch.ui.theme.metrics import (
    CARD_CONTENT_INSET,
    PATH_ROW_BUTTON_GAP,
    PATH_ROW_TRAILING_WIDTH,
    ROW_INSET,
    SMALL_ICON_SIZE,
    TOOL_BUTTON_SIZE,
)
from subsearch.ui.theme.typography import (
    CAPTION_FONT_SIZE,
    DISABLED_TEXT_COLOR,
    TEXT_COLOR,
    apply_body_font,
    body_font,
    set_error_text,
)
from subsearch.ui.widgets.anchored_popup import AnchoredPopup
from subsearch.ui.widgets.fuzzy_select import FuzzySelect
from subsearch.ui.widgets.icon_caption_button import CaptionedToolButton
from subsearch.ui.widgets.slider import SliderWithValueLabel

HELP_POPUP_MAX_WIDTH = 560
HELP_POPUP_HOVER_DELAY_MS = 300

DefaultsMap = list[tuple[str, object]]


def _resolve_default(config_key: str) -> object:
    node: object = DEFAULT_CONFIG
    for part in config_key.split("."):
        node = node[part]  # type: ignore[index]
    return node


class HelpPopup(AnchoredPopup):
    def __init__(self, explanation: str, anchor: QWidget) -> None:
        super().__init__(anchor, Qt.WindowType.ToolTip)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)

        caption_font = body_font()
        caption_font.setPixelSize(CAPTION_FONT_SIZE)

        self._message = QLabel(explanation, self)
        self._message.setWordWrap(True)
        self._message.setMaximumWidth(HELP_POPUP_MAX_WIDTH)
        self._message.setFont(caption_font)
        self._message.setStyleSheet(f"color: {TEXT_COLOR};")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.addWidget(self._message)

    def set_explanation(self, explanation: str) -> None:
        self._message.setText(explanation)


class HelpButton(TransparentToolButton):
    def __init__(
        self, explanation: str, parent: QWidget
    ) -> None:  # pyright: ignore[reportIncompatibleVariableOverride]
        super().__init__(parent)
        self.setIcon(lucide_qicon(LucideIcon.LIGHTBULB, palette.NEUTRAL_3))
        self.setFixedSize(TOOL_BUTTON_SIZE, TOOL_BUTTON_SIZE)
        self.setIconSize(QSize(SMALL_ICON_SIZE, SMALL_ICON_SIZE))
        self._popup = HelpPopup(explanation, self)
        self._hover_timer = QTimer(self)
        self._hover_timer.setSingleShot(True)
        self._hover_timer.setInterval(HELP_POPUP_HOVER_DELAY_MS)
        self._hover_timer.timeout.connect(self._popup.show_above)
        self.clicked.connect(self._popup.show_above)

    def set_explanation(self, explanation: str) -> None:
        self._popup.set_explanation(explanation)

    def enterEvent(self, e) -> None:
        self._hover_timer.start()
        super().enterEvent(e)

    def leaveEvent(self, e) -> None:
        self._hover_timer.stop()
        self._popup.hide()
        super().leaveEvent(e)


class RestoreDefaultsButton(TransparentToolButton):
    def __init__(
        self, defaults: DefaultsMap, store: SettingsStore, parent: QWidget
    ) -> None:  # pyright: ignore[reportIncompatibleVariableOverride]
        super().__init__(parent)
        self._defaults = defaults
        self._store = store
        self.setFixedSize(TOOL_BUTTON_SIZE, TOOL_BUTTON_SIZE)
        self.setIconSize(QSize(SMALL_ICON_SIZE, SMALL_ICON_SIZE))
        self._watched_keys = {key for key, _ in defaults}
        self._refresh_icon()
        self._store.value_changed.connect(lambda key, _: self._on_watched_key_changed(key))
        self.clicked.connect(self._restore_defaults)

    def _is_at_defaults(self) -> bool:
        return all(self._store.read(key) == default for key, default in self._defaults)

    def _refresh_icon(self) -> None:
        color = DISABLED_TEXT_COLOR if self._is_at_defaults() else TEXT_COLOR
        self.setIcon(lucide_qicon(LucideIcon.HISTORY, color))

    def _on_watched_key_changed(self, changed_key: str) -> None:
        if changed_key in self._watched_keys:
            self._refresh_icon()

    def _restore_defaults(self) -> None:
        for key, default in self._defaults:
            self._store.write(key, default)


class SettingRow(QFrame):
    def __init__(
        self,
        config_key: str,
        control: QWidget,
        store: SettingsStore,
        parent: QWidget | None = None,
        show_help: bool = True,
    ) -> None:
        super().__init__(parent)
        self.config_key = config_key
        self.default_value = _resolve_default(config_key)
        self.store = store
        description = SETTING_DESCRIPTIONS[config_key]

        layout = QHBoxLayout(self)
        # Right margin stays ROW_INSET so the per-row help lamp lines up with the header lamp.
        layout.setContentsMargins(CARD_CONTENT_INSET, 4, ROW_INSET, 4)
        layout.setSpacing(12)

        title_label = BodyLabel(description.title, self)
        apply_body_font(title_label)
        text_column = QVBoxLayout()
        text_column.setSpacing(2)
        text_column.addWidget(title_label)

        layout.addLayout(text_column, stretch=1)
        layout.addWidget(control, alignment=Qt.AlignmentFlag.AlignVCenter)
        self.help_button = None
        if show_help:
            self.help_button = HelpButton(description.explanation, self)
            layout.addWidget(self.help_button, alignment=Qt.AlignmentFlag.AlignVCenter)


def make_switches_mutually_exclusive(first: "SwitchRow", second: "SwitchRow") -> None:
    def uncheck_other_when_enabled(other_row: "SwitchRow"):
        def on_toggled(checked: bool) -> None:
            if checked and other_row.switch.isChecked():
                other_row.set_checked_silently(False)

        return on_toggled

    first.toggled.connect(uncheck_other_when_enabled(second))
    second.toggled.connect(uncheck_other_when_enabled(first))


class SwitchRow(SettingRow):
    toggled = Signal(bool)

    def __init__(self, config_key: str, store: SettingsStore, parent: QWidget | None = None) -> None:
        self.switch = SwitchButton()
        self.switch.setOnText("")
        self.switch.setOffText("")
        thicken_unchecked_switch_border(self.switch)
        self.switch.setChecked(bool(store.read(config_key)))
        super().__init__(config_key, self.switch, store, parent)
        self.switch.checkedChanged.connect(self._on_checked_changed)
        store.value_changed.connect(self._on_store_changed)

    def _on_checked_changed(self, checked: bool) -> None:
        self.store.write(self.config_key, checked)
        self.toggled.emit(checked)

    def _on_store_changed(self, key: str, value: object) -> None:
        if key != self.config_key:
            return
        new_checked = bool(value)
        if self.switch.isChecked() == new_checked:
            return
        self.switch.blockSignals(True)
        self.switch.setChecked(new_checked)
        self.switch.blockSignals(False)
        self.toggled.emit(new_checked)

    def set_checked_silently(self, checked: bool) -> None:
        self.switch.blockSignals(True)
        self.switch.setChecked(checked)
        self.switch.blockSignals(False)
        self.store.write(self.config_key, checked)

    def set_enabled(self, enabled: bool) -> None:
        self.switch.setEnabled(enabled)


SLIDER_ROW_CONTROL_WIDTH = 220


class SliderRow(SettingRow):
    def __init__(
        self, config_key: str, store: SettingsStore, minimum: int, maximum: int, parent: QWidget | None = None
    ) -> None:
        self.slider = SliderWithValueLabel()
        self.slider.setRange(minimum, maximum)
        self.slider.setFixedWidth(SLIDER_ROW_CONTROL_WIDTH)
        self.slider.set_value_silent(int(store.read(config_key)))
        super().__init__(config_key, self.slider, store, parent)
        self.slider.sliderReleased.connect(self._on_value_committed)
        store.value_changed.connect(self._on_store_changed)
        self._update_help(self.slider.value())

    def _on_value_committed(self) -> None:
        value = self.slider.value()
        self.store.write(self.config_key, value)
        self._update_help(value)

    def _on_store_changed(self, key: str, value: Any) -> None:
        if key != self.config_key:
            return
        self.slider.set_value_silent(int(value))
        self._update_help(int(value))

    def _update_help(self, value: int) -> None:
        if self.help_button is not None:
            self.help_button.set_explanation(SETTING_DESCRIPTIONS[self.config_key].explanation.format(limit=value))


class FuzzySelectRow(SettingRow):
    selection_changed = Signal(str)

    def __init__(
        self,
        config_key: str,
        store: SettingsStore,
        labelled_values: dict[str, str],
        aliases_by_label: dict[str, list[str]] | None = None,
        parent: QWidget | None = None,
        show_help: bool = True,
        searchable: bool = True,
    ) -> None:
        self.combo_box = FuzzySelect(searchable=searchable)
        self._value_by_label = labelled_values
        self._label_by_value = {value: label for label, value in labelled_values.items()}
        self.combo_box.setItems(list(labelled_values.keys()), aliases_by_label)
        current_value = store.read(config_key)
        if current_value in self._label_by_value:
            self.combo_box.blockSignals(True)
            self.combo_box.setCurrentText(self._label_by_value[current_value])
            self.combo_box.blockSignals(False)
        super().__init__(config_key, self.combo_box, store, parent, show_help=show_help)
        self.combo_box.currentTextChanged.connect(self._on_selection_changed)
        store.value_changed.connect(self._on_store_changed)

    def _on_selection_changed(self, label: str) -> None:
        if label not in self._value_by_label:
            return
        value = self._value_by_label[label]
        self.store.write(self.config_key, value)
        self.selection_changed.emit(value)

    def _on_store_changed(self, key: str, value: object) -> None:
        if key != self.config_key:
            return
        label = self._label_by_value.get(str(value))
        if label is None:
            return
        self.combo_box.blockSignals(True)
        self.combo_box.setCurrentText(label)
        self.combo_box.blockSignals(False)


class TrailingButtonArea(QWidget):
    """Fixed-width button column at the end of an input row. The constant width keeps
    every input field's right edge aligned across rows, no matter how many buttons a
    row carries; an optional help button stays pinned to the far right so the help
    lamps line up with the card header's lamp."""

    def __init__(
        self,
        buttons: list[QWidget],
        help_button: QWidget | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(PATH_ROW_BUTTON_GAP)
        for button in buttons:
            layout.addWidget(button)
        layout.addStretch(1)
        if help_button is not None:
            layout.addWidget(help_button)
        self.setFixedWidth(PATH_ROW_TRAILING_WIDTH)


class FolderPathRow(QWidget):
    path_saved = Signal(str, str)  # (path, detected_resolution)

    def __init__(
        self,
        config_key: str,
        store: SettingsStore,
        inline_help_text: str | None = None,
        placeholder_text: str = "",
        dialog_title: str = "Select destination folder",
        allow_empty: bool = False,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.config_key = config_key
        self.store = store
        self._allow_empty = allow_empty
        self._dialog_title = dialog_title

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(self._build_header())
        layout.addLayout(self._build_path_row(placeholder_text, inline_help_text))
        store.value_changed.connect(self._on_store_changed)

    def _on_store_changed(self, key: str, value: Any) -> None:
        if key == self.config_key and self.path_edit.text() != str(value):
            self.path_edit.setText(str(value))

    def _build_header(self) -> QHBoxLayout:
        description = SETTING_DESCRIPTIONS[self.config_key]
        title_label = BodyLabel(description.title, self)
        apply_body_font(title_label)
        header = QHBoxLayout()
        header.setContentsMargins(CARD_CONTENT_INSET, 10, ROW_INSET, 4)
        header.addWidget(title_label, stretch=1)
        header.addWidget(HelpButton(description.explanation, self))
        return header

    def _build_path_row(self, placeholder_text: str, inline_help_text: str | None) -> QHBoxLayout:
        self.path_edit = LineEdit(self)
        self.path_edit.setPlaceholderText(placeholder_text)
        self.path_edit.setText(str(self.store.read(self.config_key)))
        self.path_edit.setClearButtonEnabled(True)
        apply_body_font(self.path_edit)
        flatten_line_edit(self.path_edit)
        self.path_edit.textChanged.connect(self._on_text_changed)
        self.path_edit.editingFinished.connect(self.save_if_valid)
        self.path_edit.returnPressed.connect(self.path_edit.clearFocus)

        browse_button = CaptionedToolButton(
            "Browse", icon=lucide_qicon(LucideIcon.FOLDER_OPEN, TEXT_COLOR), parent=self
        )
        browse_button.clicked.connect(self._browse_for_folder)

        inline_help_button = HelpButton(inline_help_text, self) if inline_help_text is not None else None
        row = QHBoxLayout()
        row.setContentsMargins(CARD_CONTENT_INSET, 0, ROW_INSET, 10)
        row.addWidget(self.path_edit, stretch=1)
        row.addWidget(TrailingButtonArea([browse_button], inline_help_button, self))
        return row

    def text(self) -> str:
        return self.path_edit.text()

    def set_path(self, path: str) -> None:
        self.path_edit.setText(path)
        self.save_if_valid()

    def is_valid(self) -> bool:
        path = self.path_edit.text()
        if self._allow_empty and not path.strip():
            return True
        return release_parser.valid_path(path, release_parser.detect_path_resolution(path))

    def save_if_valid(self) -> None:
        if not self.is_valid():
            return
        path = self.path_edit.text().strip()
        self.store.write(self.config_key, path)
        self.path_saved.emit(path, release_parser.detect_path_resolution(path))

    def _on_text_changed(self, _changed_path: str) -> None:
        set_error_text(self.path_edit, not self.is_valid())

    def _browse_for_folder(self) -> None:
        selected_folder = QFileDialog.getExistingDirectory(self.window(), self._dialog_title, self.path_edit.text())
        if not selected_folder:
            return
        self.set_path(str(Path(selected_folder)))
