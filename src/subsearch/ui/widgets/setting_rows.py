from typing import NamedTuple

from PySide6.QtCore import (
    QPoint,
    QSize,
    QSortFilterProxyModel,
    Qt,
    QTimer,
    Signal,
)
from PySide6.QtGui import QPen, QStandardItem, QStandardItemModel
from PySide6.QtWidgets import (
    QApplication,
    QCompleter,
    QFrame,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)
from qfluentwidgets import (
    BodyLabel,
    ComboBox,
    EditableComboBox,
    SpinBox,
    SwitchButton,
    TransparentToolButton,
)
from qfluentwidgets.components.widgets.line_edit import CompleterMenu

from subsearch.io import toml_file
from subsearch.ui.cards.descriptions import SETTING_DESCRIPTIONS
from subsearch.ui.icons.lucide import LucideIcon, lucide_qicon
from subsearch.ui.theme.typography import (
    BODY_FONT_SIZE,
    CAPTION_FONT_SIZE,
    TEXT_COLOR,
    apply_body_font,
    body_font,
)

UNCHECKED_BORDER_WIDTH = 2
HELP_ICON_SIZE = 16
HELP_POPUP_MAX_WIDTH = 560
HELP_POPUP_GAP = 6
HELP_POPUP_HOVER_DELAY_MS = 300
MAX_VISIBLE_DROPDOWN_ITEMS = 8


class HelpPopup(QFrame):
    def __init__(self, explanation: str, anchor: QWidget) -> None:
        super().__init__(anchor.window())
        self._anchor = anchor
        self.setWindowFlags(Qt.WindowType.ToolTip | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setStyleSheet(
            "HelpPopup {"
            " background-color: #2b2b2b;"
            " border: 1px solid #454545;"
            " border-radius: 6px;"
            " }"
        )

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

    def show_above(self) -> None:
        self.adjustSize()
        anchor_top_left = self._anchor.mapToGlobal(QPoint(0, 0))
        anchor_center_x = anchor_top_left.x() + self._anchor.width() // 2
        anchor_bottom = anchor_top_left.y() + self._anchor.height()

        screen = self.screen() or QApplication.screenAt(anchor_top_left)
        screen_area = screen.availableGeometry()

        x = anchor_center_x - self.width() // 2
        x = max(screen_area.left(), min(x, screen_area.right() - self.width() + 1))

        y = anchor_top_left.y() - self.height() - HELP_POPUP_GAP
        if y < screen_area.top():
            y = anchor_bottom + HELP_POPUP_GAP
        y = max(screen_area.top(), min(y, screen_area.bottom() - self.height() + 1))

        self.move(QPoint(x, y))
        self.show()
        self.raise_()


class HelpButton(TransparentToolButton):
    def __init__(self, explanation: str, parent: QWidget) -> None:  # pyright: ignore[reportIncompatibleVariableOverride]
        super().__init__(parent)
        self.setIcon(lucide_qicon(LucideIcon.LIGHTBULB, TEXT_COLOR))
        self.setFixedSize(32, 32)
        self.setIconSize(QSize(HELP_ICON_SIZE, HELP_ICON_SIZE))
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


def style_dropdown_menu(menu, object_name: str) -> None:
    font = body_font()
    menu.view.setFont(font)
    for action in menu.actions():
        action.setFont(font)
    menu.view.setStyleSheet(
        f"#{object_name} {{ color: {TEXT_COLOR}; font-size: {BODY_FONT_SIZE}px; }}"
    )


class BodyFontComboBox(ComboBox):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setMaxVisibleItems(MAX_VISIBLE_DROPDOWN_ITEMS)

    def _showComboMenu(self) -> None:
        super()._showComboMenu()
        if self.dropMenu is None:
            return
        style_dropdown_menu(self.dropMenu, "comboListWidget")


SEARCH_TERMS_ROLE = Qt.ItemDataRole.UserRole + 1


class MatchRank(NamedTuple):
    tier: int
    label_length: int


def rank_match(terms: list[str], query: str) -> MatchRank:
    query_lower = query.lower()
    best_tier = 3
    for term in terms:
        term_lower = term.lower()
        if term_lower == query_lower:
            best_tier = min(best_tier, 0)
        elif term_lower.startswith(query_lower):
            best_tier = min(best_tier, 1)
        elif query_lower in term_lower:
            best_tier = min(best_tier, 2)
    return MatchRank(best_tier, len(terms[0]))


def best_matching_label(search_terms_by_label: dict[str, list[str]], query: str) -> str | None:
    if not query:
        return None
    ranked = min(
        search_terms_by_label,
        key=lambda label: rank_match(search_terms_by_label[label], query),
    )
    if rank_match(search_terms_by_label[ranked], query).tier == 3:
        return None
    return ranked


class SearchTermsFilterProxy(QSortFilterProxyModel):
    def filterAcceptsRow(self, source_row: int, source_parent) -> bool:
        index = self.sourceModel().index(source_row, 0, source_parent)
        query = self.filterRegularExpression().pattern().lower()
        if not query:
            return True
        terms = self.sourceModel().data(index, SEARCH_TERMS_ROLE) or []
        return any(query in term.lower() for term in terms)


class SearchableComboBox(EditableComboBox):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setMaxVisibleItems(MAX_VISIBLE_DROPDOWN_ITEMS)
        self._search_terms_by_label: dict[str, list[str]] = {}

    def setItems(self, labels: list[str], aliases_by_label: dict[str, list[str]] | None = None) -> None:
        aliases_by_label = aliases_by_label or {}
        self._search_terms_by_label = {
            label: [label, *aliases_by_label.get(label, [])] for label in labels
        }
        self.addItems(labels)

        model = QStandardItemModel(self)
        for label, terms in self._search_terms_by_label.items():
            item = QStandardItem(label)
            item.setData(terms, SEARCH_TERMS_ROLE)
            model.appendRow(item)

        self._filter_proxy = SearchTermsFilterProxy(self)
        self._filter_proxy.setSourceModel(model)

        completer = QCompleter(self._filter_proxy, self)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.setCompletionMode(QCompleter.CompletionMode.UnfilteredPopupCompletion)
        completer.setMaxVisibleItems(MAX_VISIBLE_DROPDOWN_ITEMS)
        self.setCompleter(completer)

    def _showCompleterMenu(self) -> None:
        if not self.completer() or not self.text():
            return
        self._filter_proxy.setFilterFixedString(self.text())
        if self._completerMenu is None:
            self.setCompleterMenu(CompleterMenu(self))
            style_dropdown_menu(self._completerMenu, "completerListWidget")
        self.completer().setCompletionPrefix("")
        changed = self._completerMenu.setCompletion(
            self.completer().completionModel(), self.completer().completionColumn()
        )
        self._completerMenu.setMaxVisibleItems(self.completer().maxVisibleItems())
        if changed:
            self._completerMenu.popup()
        self._highlight_best_completion()

    def _highlight_best_completion(self) -> None:
        match = best_matching_label(self._search_terms_by_label, self.text())
        view = self._completerMenu.view
        if match is None:
            view.setCurrentRow(-1)
            return
        row = self._completerMenu.items.index(match) if match in self._completerMenu.items else -1
        view.setCurrentRow(row)

    def _onReturnPressed(self) -> None:
        match = best_matching_label(self._search_terms_by_label, self.text())
        if match is None:
            return
        self.setCurrentIndex(self.findText(match))
        if self._completerMenu:
            self._completerMenu.close()

    def _showComboMenu(self) -> None:
        super()._showComboMenu()
        if self.dropMenu is None:
            return
        style_dropdown_menu(self.dropMenu, "comboListWidget")


def thicken_unchecked_switch_border(switch: SwitchButton) -> None:
    indicator = switch.indicator
    radius = indicator.height() / 2

    def draw_background(painter) -> None:
        if indicator.isChecked():
            painter.setPen(indicator._borderColor())
        else:
            pen = QPen(indicator._borderColor())
            pen.setWidth(UNCHECKED_BORDER_WIDTH)
            painter.setPen(pen)
        painter.setBrush(indicator._backgroundColor())
        painter.drawRoundedRect(indicator.rect().adjusted(1, 1, -1, -1), radius, radius)

    indicator._drawBackground = draw_background


class SettingRow(QFrame):
    def __init__(
        self,
        config_key: str,
        control: QWidget,
        parent: QWidget | None = None,
        show_help: bool = True,
    ) -> None:
        super().__init__(parent)
        self.config_key = config_key
        description = SETTING_DESCRIPTIONS[config_key]

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 4, 16, 4)
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


def read_value(config_key: str):
    return toml_file.get_config_session().read(config_key)


def write_value(config_key: str, value) -> None:
    toml_file.get_config_session().write(config_key, value)


class SwitchRow(SettingRow):
    toggled = Signal(bool)

    def __init__(self, config_key: str, parent: QWidget | None = None) -> None:
        self.switch = SwitchButton()
        self.switch.setOnText("")
        self.switch.setOffText("")
        thicken_unchecked_switch_border(self.switch)
        self.switch.setChecked(bool(read_value(config_key)))
        super().__init__(config_key, self.switch, parent)
        self.switch.checkedChanged.connect(self._on_checked_changed)

    def _on_checked_changed(self, checked: bool) -> None:
        write_value(self.config_key, checked)
        self.toggled.emit(checked)

    def set_checked_silently(self, checked: bool) -> None:
        self.switch.blockSignals(True)
        self.switch.setChecked(checked)
        self.switch.blockSignals(False)
        write_value(self.config_key, checked)

    def set_enabled(self, enabled: bool) -> None:
        self.switch.setEnabled(enabled)


class SpinBoxRow(SettingRow):
    def __init__(
        self, config_key: str, minimum: int, maximum: int, parent: QWidget | None = None
    ) -> None:
        self.spin_box = SpinBox()
        apply_body_font(self.spin_box)
        self.spin_box.setRange(minimum, maximum)
        self.spin_box.setValue(int(read_value(config_key)))
        self.spin_box.setFixedWidth(120)
        super().__init__(config_key, self.spin_box, parent)
        self.spin_box.valueChanged.connect(self._on_value_changed)
        self._update_help(self.spin_box.value())

    def _on_value_changed(self, value: int) -> None:
        write_value(self.config_key, value)
        self._update_help(value)

    def _update_help(self, value: int) -> None:
        if self.help_button is not None:
            self.help_button.set_explanation(SETTING_DESCRIPTIONS[self.config_key].explanation.format(limit=value))


class ComboBoxRow(SettingRow):
    selection_changed = Signal(str)

    def __init__(
        self,
        config_key: str,
        labelled_values: dict[str, str],
        parent: QWidget | None = None,
    ) -> None:
        self.combo_box = BodyFontComboBox()
        apply_body_font(self.combo_box)
        self.combo_box.setFixedWidth(160)
        self._value_by_label = labelled_values
        self._label_by_value = {value: label for label, value in labelled_values.items()}
        self.combo_box.addItems(list(labelled_values.keys()))
        current_value = read_value(config_key)
        if current_value in self._label_by_value:
            self.combo_box.setCurrentText(self._label_by_value[current_value])
        super().__init__(config_key, self.combo_box, parent)
        self.combo_box.currentTextChanged.connect(self._on_selection_changed)

    def _on_selection_changed(self, label: str) -> None:
        value = self._value_by_label[label]
        write_value(self.config_key, value)
        self.selection_changed.emit(value)


class SearchableComboBoxRow(SettingRow):
    selection_changed = Signal(str)

    def __init__(
        self,
        config_key: str,
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
        current_value = read_value(config_key)
        if current_value in self._label_by_value:
            self.combo_box.setCurrentText(self._label_by_value[current_value])
        super().__init__(config_key, self.combo_box, parent, show_help=show_help)
        self.combo_box.currentTextChanged.connect(self._on_selection_changed)

    def _on_selection_changed(self, label: str) -> None:
        if label not in self._value_by_label:
            return
        value = self._value_by_label[label]
        write_value(self.config_key, value)
        self.selection_changed.emit(value)
