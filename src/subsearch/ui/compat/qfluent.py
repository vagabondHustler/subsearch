"""Every qfluentwidgets private-API touch and monkeypatch lives here.

qfluentwidgets (PySide6-Fluent-Widgets, pinned in pyproject.toml) does not expose
public hooks for the visual adjustments Subsearch needs, so each section below
reaches into private internals. When upgrading the library, re-verify this file
first - nothing outside ui/compat/ may touch a private qfluentwidgets attribute.
"""

from typing import NamedTuple

from PySide6.QtCore import QPoint, QRect, QRectF, QSortFilterProxyModel, Qt
from PySide6.QtGui import (
    QColor,
    QCursor,
    QPainter,
    QPen,
    QStandardItem,
    QStandardItemModel,
)
from PySide6.QtWidgets import QCompleter, QWidget
from qfluentwidgets import (
    ComboBox,
    EditableComboBox,
    NavigationPanel,
    Slider,
    SwitchButton,
    ThemeColor,
)
from qfluentwidgets.common.color import autoFallbackThemeColor
from qfluentwidgets.common.icon import drawIcon, isDarkTheme
from qfluentwidgets.components.widgets.line_edit import CompleterMenu
from qfluentwidgets.components.widgets.slider import SliderHandle

from subsearch.ui.icons.lucide import LucideIcon
from subsearch.ui.theme import palette
from subsearch.ui.theme.typography import BODY_FONT_SIZE, TEXT_COLOR, body_font

# --- Fixed accent color -------------------------------------------------------
# qfluentwidgets derives light/dark accent variants from the saved theme color;
# replacing ThemeColor.color is the only way to pin every variant to our
# neutral accent without it shifting between widget states.

ACCENT_COLOR = palette.NEUTRAL_1

_BRIGHTNESS_BY_VARIANT = {
    ThemeColor.PRIMARY: 1.0,
    ThemeColor.DARK_1: 0.9,
    ThemeColor.DARK_2: 0.82,
    ThemeColor.DARK_3: 0.7,
    ThemeColor.LIGHT_1: 1.0,
    ThemeColor.LIGHT_2: 1.0,
    ThemeColor.LIGHT_3: 1.0,
}


def _fixed_accent_color(self: ThemeColor) -> QColor:
    accent = QColor(ACCENT_COLOR)
    hue, saturation, value = accent.hueF(), accent.saturationF(), accent.valueF()
    value = min(value * _BRIGHTNESS_BY_VARIANT[self], 1.0)
    return QColor.fromHsvF(hue, saturation, value)


def force_fixed_accent_color() -> None:
    ThemeColor.color = _fixed_accent_color


# --- Navigation items with larger icons ---------------------------------------
# NavigationPushButton hardcodes a 16px icon rect in its paintEvent; there is no
# icon-size setter, so the paint routine is replaced per item. Reads private
# item state (_margins, _icon, _canDrawIndicator, isCompacted).

NAVIGATION_ICON_SIZE = 24
NAVIGATION_ITEM_HEIGHT = 36


def _paint_navigation_item_with_large_icon(item, _event) -> None:
    painter = QPainter(item)
    try:
        painter.setRenderHints(
            QPainter.RenderHint.Antialiasing
            | QPainter.RenderHint.TextAntialiasing
            | QPainter.RenderHint.SmoothPixmapTransform
        )
        painter.setPen(Qt.PenStyle.NoPen)

        if item.isPressed:
            painter.setOpacity(0.7)
        if not item.isEnabled():
            painter.setOpacity(0.4)

        background = 255 if isDarkTheme() else 0
        margins = item._margins()
        padding_left, padding_right = margins.left(), margins.right()
        global_rect = QRect(item.mapToGlobal(QPoint()), item.size())

        if item._canDrawIndicator():
            painter.setBrush(QColor(background, background, background, 6 if item.isEnter else 10))
            painter.drawRoundedRect(item.rect(), 5, 5)
            painter.setBrush(autoFallbackThemeColor(item.lightIndicatorColor, item.darkIndicatorColor))
            painter.drawRoundedRect(item.indicatorRect(), 1.5, 1.5)
        elif ((item.isEnter and global_rect.contains(QCursor.pos())) or item.isAboutSelected) and item.isEnabled():
            painter.setBrush(QColor(background, background, background, 6 if item.isAboutSelected else 10))
            painter.drawRoundedRect(item.rect(), 5, 5)

        icon_top = (NAVIGATION_ITEM_HEIGHT - NAVIGATION_ICON_SIZE) / 2
        icon_rect = QRectF(7.5 + padding_left, icon_top, NAVIGATION_ICON_SIZE, NAVIGATION_ICON_SIZE)
        if isinstance(item._icon, LucideIcon):
            item._icon.render(painter, icon_rect, stroke=TEXT_COLOR)
        else:
            drawIcon(item._icon, painter, icon_rect)

        if item.isCompacted:
            return

        painter.setFont(item.font())
        painter.setPen(item.textColor())
        text_left = 44 + padding_left if not item.icon().isNull() else padding_left + 16
        painter.drawText(
            QRectF(text_left, 0, item.width() - 13 - text_left - padding_right, item.height()),
            Qt.AlignmentFlag.AlignVCenter,
            item.text(),
        )
    finally:
        painter.end()


def enlarge_navigation_icons(panel: NavigationPanel) -> None:
    items = [panel.menuButton, panel.returnButton]
    for navigation_item in panel.items.values():
        items.append(getattr(navigation_item.widget, "itemWidget"))
    for item in items:
        item.paintEvent = lambda e, item=item: _paint_navigation_item_with_large_icon(item, e)
        item.update()


# --- Switch border -------------------------------------------------------------
# The unchecked switch border is 1px and nearly invisible on the dark theme;
# the indicator exposes no border-width property, so its private
# _drawBackground is replaced.

UNCHECKED_BORDER_WIDTH = 2


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


# --- Circle-dot slider handle ----------------------------------------------------
# Slider builds its handle in the private _postInit and offers no handle
# factory, so the stock handle is deleted and replaced; dragging maps back to
# values through the private _posToValue.

HANDLE_SIZE = 32
HANDLE_CENTER = HANDLE_SIZE // 2
HANDLE_RADIUS = 8
HANDLE_FILL_COLOR = QColor(palette.SLIDER_HANDLE_FILL)
HANDLE_BORDER_COLOR = QColor(palette.SLIDER_HANDLE_BORDER)
HANDLE_BORDER_WIDTH = 2
HOVER_DISC_RADIUS = 14
HOVER_DISC_COLOR = QColor(255, 255, 255, 21)
PRESSED_DISC_COLOR = QColor(255, 255, 255, 12)


class CircleDotHandle(SliderHandle):
    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.setFixedSize(HANDLE_SIZE, HANDLE_SIZE)
        self._hovered = False
        self._pressed = False

    def enterEvent(self, e) -> None:
        self._hovered = True
        self.update()

    def leaveEvent(self, e) -> None:
        self._hovered = False
        self.update()

    def mousePressEvent(self, e) -> None:
        self._pressed = True
        self.update()
        self.pressed.emit()
        self._drag_to(e)

    def mouseMoveEvent(self, e) -> None:
        self._drag_to(e)

    def mouseReleaseEvent(self, e) -> None:
        self._pressed = False
        self.update()
        self.released.emit()

    def _drag_to(self, e) -> None:
        self.parent().update_value_from_handle(e.position().toPoint())

    def paintEvent(self, e) -> None:
        center = QPoint(HANDLE_CENTER, HANDLE_CENTER)
        painter = QPainter(self)
        painter.setRenderHints(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)

        if self._pressed:
            painter.setBrush(PRESSED_DISC_COLOR)
            painter.drawEllipse(center, HOVER_DISC_RADIUS, HOVER_DISC_RADIUS)
        elif self._hovered:
            painter.setBrush(HOVER_DISC_COLOR)
            painter.drawEllipse(center, HOVER_DISC_RADIUS, HOVER_DISC_RADIUS)

        painter.setPen(QPen(HANDLE_BORDER_COLOR, HANDLE_BORDER_WIDTH))
        painter.setBrush(HANDLE_FILL_COLOR)
        painter.drawEllipse(center, HANDLE_RADIUS, HANDLE_RADIUS)


class CircleDotSlider(Slider):
    def _postInit(self) -> None:
        super()._postInit()
        self.handle.deleteLater()
        self.handle = CircleDotHandle(self)
        self.handle.pressed.connect(self.sliderPressed)
        self.handle.released.connect(self.sliderReleased)
        self.handle.setHandleColor(self.lightGrooveColor, self.darkGrooveColor)
        self.setMinimumHeight(HANDLE_SIZE)
        self._adjustHandlePos()

    def update_value_from_handle(self, handle_position: QPoint) -> None:
        self.setValue(self._posToValue(self.handle.mapToParent(handle_position)))

    def set_value_silent(self, value: int) -> None:
        """Set value without emitting valueChanged; repositions the handle manually."""
        self.blockSignals(True)
        self.setValue(value)
        self._adjustHandlePos()
        self.blockSignals(False)


# --- Styled dropdown / completer menus -------------------------------------------
# Combo menus ignore the application font and text color; menu.view and the
# private _showComboMenu/_completerMenu hooks are the only access points.

MAX_VISIBLE_DROPDOWN_ITEMS = 8


def style_dropdown_menu(menu, object_name: str) -> None:
    font = body_font()
    menu.view.setFont(font)
    for action in menu.actions():
        action.setFont(font)
    menu.view.setStyleSheet(f"#{object_name} {{ color: {TEXT_COLOR}; font-size: {BODY_FONT_SIZE}px; }}")


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
        self._search_terms_by_label = {label: [label, *aliases_by_label.get(label, [])] for label in labels}
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
