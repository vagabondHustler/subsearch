"""Every qfluentwidgets private-API touch and monkeypatch lives here.

qfluentwidgets (PySide6-Fluent-Widgets, pinned in pyproject.toml) does not expose
public hooks for the visual adjustments Subsearch needs, so each section below
reaches into private internals. When upgrading the library, re-verify this file
first - nothing outside ui/compat/ may touch a private qfluentwidgets attribute.
"""

from typing import cast

from PySide6.QtCore import QEvent, QObject, QPoint, QRect, QRectF, Qt
from PySide6.QtGui import QColor, QCursor, QPainter, QPen
from PySide6.QtWidgets import QAbstractScrollArea, QApplication, QWidget
from qfluentwidgets import LineEdit, NavigationPanel, Slider, SwitchButton, ThemeColor
from qfluentwidgets.common.color import autoFallbackThemeColor
from qfluentwidgets.common.icon import drawIcon, isDarkTheme
from qfluentwidgets.components.widgets.slider import SliderHandle

from subsearch.ui.icons.lucide import LucideIcon
from subsearch.ui.theme import palette
from subsearch.ui.theme.typography import TEXT_COLOR, append_custom_style

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


# --- Navigation wheel forwarding -----------------------------------------------
# The navigation panel swallows wheel events instead of letting them scroll the
# page beside it. NavigationPanel exposes no scroll-passthrough hook, so an event
# filter intercepts wheel events over the panel and replays them on the current
# page's scroll area viewport.


class _NavigationWheelForwarder(QObject):
    def __init__(self, panel: NavigationPanel, page_provider) -> None:
        super().__init__(panel)
        self._page_provider = page_provider

    def eventFilter(self, _watched, event) -> bool:
        if event.type() != QEvent.Type.Wheel:
            return False
        page = self._page_provider()
        scroll_area = page.findChild(QAbstractScrollArea) if page is not None else None
        if scroll_area is None:
            return False
        QApplication.sendEvent(scroll_area.viewport(), event)
        return True


def forward_navigation_wheel_to_page(panel: NavigationPanel, page_provider) -> None:
    forwarder = _NavigationWheelForwarder(panel, page_provider)
    panel.installEventFilter(forwarder)


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


# --- Borderless line edit --------------------------------------------------------
# LineEdit paints a focused accent underline directly in paintEvent (not via QSS),
# so a stylesheet "border: none" cannot remove it; the only hook is the color the
# paint uses, so focusedBorderColor is forced transparent.


def hide_line_edit_focus_underline(line_edit: LineEdit) -> None:
    line_edit.focusedBorderColor = lambda: QColor(Qt.GlobalColor.transparent)


# The brighter resting bottom underline comes from qfluent's LINE_EDIT QSS
# (border-bottom at ~0.54 alpha vs 0.08 for the other edges); the rule below
# matches the bottom edge to the other three.
_UNIFORM_BORDER_QSS = " LineEdit { border-bottom: 1px solid rgba(255, 255, 255, 0.08); }"
_CHROMELESS_QSS = " LineEdit { background: transparent; border: none; }"


def flatten_line_edit(line_edit: LineEdit) -> None:
    """Replace the bright bottom underline with the same thin 1px border as the
    other edges, and hide the painted focus underline. Registered as custom QSS
    because the StyleSheetManager wipes plain setStyleSheet on its re-applies."""
    append_custom_style(line_edit, _UNIFORM_BORDER_QSS)
    hide_line_edit_focus_underline(line_edit)


def make_line_edit_chromeless(line_edit: LineEdit) -> None:
    """No background, border, or underline at all (the slider's value edit)."""
    append_custom_style(line_edit, _CHROMELESS_QSS)
    hide_line_edit_focus_underline(line_edit)


# --- Trailing widget inside a line edit ------------------------------------------
# LineEdit lays its clear button out in a private hBoxLayout pinned to the right
# edge; embedding our own button there is the only way to sit a control inside the
# field. We reserve right text margin for it so typed text never runs underneath.


def embed_trailing_widget(line_edit: LineEdit, widget: QWidget, reserved_width: int) -> None:
    line_edit.hBoxLayout.addWidget(widget, 0, Qt.AlignmentFlag.AlignRight)
    margins = line_edit.textMargins()
    line_edit.setTextMargins(margins.left(), margins.top(), reserved_width, margins.bottom())


# --- Acrylic popups -------------------------------------------------------------
# Qt cannot blur what is behind a window; the acrylic backdrop comes from the
# Windows compositor via qframelesswindow's WindowsWindowEffect, and the rounded
# corners from DWM (attribute 33), since the QSS border-radius cannot clip the
# compositor-drawn backdrop.

# RGBA tint over the blurred backdrop; POPUP_BACKGROUND at ~70% opacity.
_ACRYLIC_TINT = palette.POPUP_BACKGROUND.lstrip("#") + "B3"
_DWMWA_WINDOW_CORNER_PREFERENCE = 33
_DWMWCP_ROUND = 2


def apply_popup_acrylic(popup) -> bool:
    # The caller must set WA_TranslucentBackground before the native window exists
    # (i.e. in __init__): toggling it on a live window leaves the surface without an
    # alpha channel while disabling background erase, so repaints smear over each other.
    import ctypes

    from qframelesswindow.windows.window_effect import (  # type: ignore[import-untyped]
        WindowsWindowEffect,
    )

    try:
        window_handle = int(popup.winId())
        effect = WindowsWindowEffect(popup)
        effect.setAcrylicEffect(window_handle, _ACRYLIC_TINT)
        corner_preference = ctypes.c_int(_DWMWCP_ROUND)
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            window_handle,
            _DWMWA_WINDOW_CORNER_PREFERENCE,
            ctypes.byref(corner_preference),
            ctypes.sizeof(corner_preference),
        )
        return True
    except OSError, AttributeError:
        # Compositor effects are unavailable (offscreen rendering, older Windows);
        # the caller falls back to painting an opaque background instead.
        return False


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
        self._press_offset = QPoint()

    def enterEvent(self, e) -> None:
        self._hovered = True
        self.update()

    def leaveEvent(self, e) -> None:
        self._hovered = False
        self.update()

    def mousePressEvent(self, e) -> None:
        self._pressed = True
        # Remember where on the handle the press landed so an off-center grab
        # does not jump the value; only drags move it.
        self._press_offset = e.position().toPoint() - QPoint(HANDLE_CENTER, HANDLE_CENTER)
        self.update()
        self.pressed.emit()

    def mouseMoveEvent(self, e) -> None:
        slider = cast("CircleDotSlider", self.parent())
        slider.update_value_from_handle(e.position().toPoint() - self._press_offset)

    def mouseReleaseEvent(self, e) -> None:
        self._pressed = False
        self.update()
        self.released.emit()

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
    handle: "CircleDotHandle"

    def _postInit(self) -> None:
        super()._postInit()
        self.handle.deleteLater()
        self.handle = CircleDotHandle(self)
        self.handle.pressed.connect(self.sliderPressed)
        self.handle.released.connect(self.sliderReleased)
        self.handle.setHandleColor(self.lightGrooveColor, self.darkGrooveColor)
        self.setMinimumHeight(HANDLE_SIZE)
        self._adjustHandlePos()

    def _drawHorizonGroove(self, painter: QPainter) -> None:
        # qfluent's groove paints a colored fill up to the handle; we draw only the
        # plain base groove so no accent-colored line appears under the value.
        width, radius = self.width(), self.handle.width() / 2
        painter.drawRoundedRect(QRectF(radius, radius - 2, width - radius * 2, 4), 2, 2)

    def update_value_from_handle(self, handle_position: QPoint) -> None:
        self.setValue(self._posToValue(self.handle.mapToParent(handle_position)))

    def set_value_silent(self, value: int) -> None:
        """Set value without emitting valueChanged; repositions the handle manually."""
        self.blockSignals(True)
        self.setValue(value)
        self._adjustHandlePos()
        self.blockSignals(False)
