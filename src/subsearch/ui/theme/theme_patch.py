from PySide6.QtGui import QColor
from qfluentwidgets import ThemeColor

ACCENT_COLOR = "#c8c8c7"

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
