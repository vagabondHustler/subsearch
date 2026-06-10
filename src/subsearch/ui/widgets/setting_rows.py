from PySide6.QtCore import QSize, Qt, QTimer, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)
from qfluentwidgets import (
    BodyLabel,
    SpinBox,
    SwitchButton,
    TransparentToolButton,
)

from subsearch.runtime.config.constants import DEFAULT_CONFIG
from subsearch.ui.cards.descriptions import SETTING_DESCRIPTIONS
from subsearch.ui.compat.qfluent import (
    SearchableComboBox,
    thicken_unchecked_switch_border,
)
from subsearch.ui.icons.lucide import LucideIcon, lucide_qicon
from subsearch.ui.state.store import SettingsStore
from subsearch.ui.theme import palette
from subsearch.ui.theme.metrics import ROW_INSET, SMALL_ICON_SIZE, TOOL_BUTTON_SIZE
from subsearch.ui.theme.typography import (
    CAPTION_FONT_SIZE,
    DISABLED_TEXT_COLOR,
    TEXT_COLOR,
    apply_body_font,
    body_font,
)
from subsearch.ui.widgets.anchored_popup import AnchoredPopup

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
        layout.setContentsMargins(ROW_INSET, 4, ROW_INSET, 4)
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


class SpinBoxRow(SettingRow):
    def __init__(
        self, config_key: str, store: SettingsStore, minimum: int, maximum: int, parent: QWidget | None = None
    ) -> None:
        self.spin_box = SpinBox()
        apply_body_font(self.spin_box)
        self.spin_box.setRange(minimum, maximum)
        self.spin_box.setValue(int(store.read(config_key)))
        self.spin_box.setFixedWidth(120)
        super().__init__(config_key, self.spin_box, store, parent)
        self.spin_box.valueChanged.connect(self._on_value_changed)
        store.value_changed.connect(self._on_store_changed)
        self._update_help(self.spin_box.value())

    def _on_value_changed(self, value: int) -> None:
        self.store.write(self.config_key, value)
        self._update_help(value)

    def _on_store_changed(self, key: str, value: object) -> None:
        if key != self.config_key:
            return
        self.spin_box.blockSignals(True)
        self.spin_box.setValue(int(value))
        self.spin_box.blockSignals(False)
        self._update_help(int(value))

    def _update_help(self, value: int) -> None:
        if self.help_button is not None:
            self.help_button.set_explanation(SETTING_DESCRIPTIONS[self.config_key].explanation.format(limit=value))


class SearchableComboBoxRow(SettingRow):
    selection_changed = Signal(str)

    def __init__(
        self,
        config_key: str,
        store: SettingsStore,
        labelled_values: dict[str, str],
        aliases_by_label: dict[str, list[str]] | None = None,
        parent: QWidget | None = None,
        show_help: bool = True,
    ) -> None:
        self.combo_box = SearchableComboBox()
        apply_body_font(self.combo_box)
        self.combo_box.setFixedWidth(200)
        self._value_by_label = labelled_values
        self._label_by_value = {value: label for label, value in labelled_values.items()}
        self.combo_box.setItems(list(labelled_values.keys()), aliases_by_label)
        current_value = store.read(config_key)
        if current_value in self._label_by_value:
            self.combo_box.setCurrentText(self._label_by_value[current_value])
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
