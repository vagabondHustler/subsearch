from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import QWidget
from qfluentwidgets import CustomStyleSheet, setCustomStyleSheet, setFont

from subsearch.ui.theme import palette

BODY_FONT_SIZE = 12
CAPTION_FONT_SIZE = 12
SUBSECTION_FONT_SIZE = 10
TOKEN_HEADER_FONT_SIZE = 12
TOKEN_VALUE_FONT_SIZE = 12
TITLE_FONT_SIZE = 14
SEMI_BOLD = QFont.Weight.DemiBold
TEXT_COLOR = palette.NEUTRAL_1
SUBTLE_TEXT_COLOR = palette.NEUTRAL_2
MUTED_TEXT_COLOR = palette.NEUTRAL_3
DISABLED_TEXT_COLOR = palette.NEUTRAL_4
ERROR_TEXT_COLOR = palette.RED
SUCCESS_TEXT_COLOR = palette.GREEN


def body_font() -> QFont:
    font = QFont()
    font.setPixelSize(BODY_FONT_SIZE)
    font.setWeight(SEMI_BOLD)
    return font


def append_custom_style(widget: QWidget, qss: str) -> None:
    """Register qss with qfluent's StyleSheetManager so it survives the manager's
    QSS re-applies, which silently wipe anything set via plain setStyleSheet."""
    existing = CustomStyleSheet(widget)
    setCustomStyleSheet(widget, existing.lightStyleSheet() + qss, existing.darkStyleSheet() + qss)


def set_three_state_text_color(widget: QWidget) -> None:
    widget_type = type(widget).__name__
    qss = (
        f"{widget_type} {{ color: {TEXT_COLOR}; }}"
        f"{widget_type}:disabled {{ color: {DISABLED_TEXT_COLOR}; }}"
        f'{widget_type}[error="true"] {{ color: {ERROR_TEXT_COLOR}; }}'
    )
    widget.setStyleSheet(qss)
    append_custom_style(widget, qss)


def set_error_text(widget: QWidget, has_error: bool) -> None:
    widget.setProperty("error", has_error)
    widget.style().unpolish(widget)
    widget.style().polish(widget)


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


def apply_subsection_font(widget: QWidget) -> None:
    setFont(widget, SUBSECTION_FONT_SIZE, SEMI_BOLD)
    apply_text_color(widget)


def apply_title_font(widget: QWidget) -> None:
    setFont(widget, TITLE_FONT_SIZE, SEMI_BOLD)
    apply_text_color(widget)


def apply_section_label_font(widget: QWidget) -> None:
    setFont(widget, CAPTION_FONT_SIZE, QFont.Weight.Normal)
    apply_text_color(widget)


def apply_label_color(widget: QWidget, color: str) -> None:
    widget.setStyleSheet(f"color: {color};")


def apply_token_row_label_font(widget: QWidget) -> None:
    setFont(widget, TOKEN_HEADER_FONT_SIZE, SEMI_BOLD)
    apply_label_color(widget, TEXT_COLOR)


def apply_token_header_font(widget: QWidget) -> None:
    setFont(widget, TOKEN_HEADER_FONT_SIZE, SEMI_BOLD)
    apply_label_color(widget, SUBTLE_TEXT_COLOR)


def apply_token_value_font(widget: QWidget) -> None:
    setFont(widget, TOKEN_VALUE_FONT_SIZE, SEMI_BOLD)
    qss = f"{type(widget).__name__} {{ color: {MUTED_TEXT_COLOR}; }}"
    widget.setStyleSheet(qss)
    append_custom_style(widget, qss)
