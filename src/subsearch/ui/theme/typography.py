from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import QWidget
from qfluentwidgets import setFont

BODY_FONT_SIZE = 12
CAPTION_FONT_SIZE = 11
TITLE_FONT_SIZE = 14
SEMI_BOLD = QFont.Weight.DemiBold
TEXT_COLOR = "#c8c8c7"
DISABLED_TEXT_COLOR = "#5a5a5a"
ERROR_TEXT_COLOR = "#e85b5b"


def body_font() -> QFont:
    font = QFont()
    font.setPixelSize(BODY_FONT_SIZE)
    font.setWeight(SEMI_BOLD)
    return font


def set_three_state_text_color(widget: QWidget) -> None:
    widget_type = type(widget).__name__
    widget.setStyleSheet(
        f"{widget_type} {{ color: {TEXT_COLOR}; }}"
        f"{widget_type}:disabled {{ color: {DISABLED_TEXT_COLOR}; }}"
        f'{widget_type}[error="true"] {{ color: {ERROR_TEXT_COLOR}; }}'
    )


def apply_text_color(widget: QWidget) -> None:
    color = QColor(TEXT_COLOR)
    set_text_color = getattr(widget, "setTextColor", None)
    if set_text_color is not None:
        set_text_color(color, color)
    else:
        set_three_state_text_color(widget)


def apply_body_font(widget: QWidget) -> None:
    setFont(widget, BODY_FONT_SIZE, SEMI_BOLD)
    apply_text_color(widget)


def apply_caption_font(widget: QWidget) -> None:
    setFont(widget, CAPTION_FONT_SIZE, SEMI_BOLD)
    apply_text_color(widget)


def apply_title_font(widget: QWidget) -> None:
    setFont(widget, TITLE_FONT_SIZE, SEMI_BOLD)
    apply_text_color(widget)
