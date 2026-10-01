from dataclasses import dataclass
from typing import Any

from PySide6.QtCore import QRect, QSize, Qt
from PySide6.QtGui import QColor, QFont, QFontMetrics, QPainter
from PySide6.QtWidgets import QAbstractButton, QWidget

from subsearch.ui.icons.lucide import LucideIcon, lucide_pixmap
from subsearch.ui.theme import palette
from subsearch.ui.theme.metrics import TOOL_ICON_SIZE
from subsearch.ui.theme.typography import (
    CAPTION_FONT_SIZE,
    DISABLED_TEXT_COLOR,
    SEMI_BOLD,
    TEXT_COLOR,
)

# Visible gap between the glyph and the cap height of the caption text.
CAPTION_GAP = 3
# Invisible padding above the glyph so it doesn't sit flush against the top edge.
GLYPH_TOP_PADDING = 2


# Mouse-over lightens the glyph and caption; a press darkens them.
HOVER_LIGHTER = 130
PRESS_DARKER = 130


@dataclass(frozen=True, slots=True)
class CaptionToolButtonStyle:
    icon: LucideIcon
    caption: str
    color: str = TEXT_COLOR
    icon_size: int = TOOL_ICON_SIZE
    caption_font_size: int = CAPTION_FONT_SIZE


class CaptionToolButton(QAbstractButton):
    def __init__(self, style: CaptionToolButtonStyle, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._style = style
        self._hovered = False

        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._font = QFont()
        self._font.setPointSize(style.caption_font_size)
        self._font.setWeight(SEMI_BOLD)

    def _caption(self) -> str:
        return self._style.caption

    def _base_color(self) -> QColor:
        return QColor(self._style.color)

    def _captions(self) -> tuple[str, ...]:
        return (self._style.caption,)

    def _state_color(self) -> QColor:
        color = self._base_color()
        if self.isDown():
            return color.darker(PRESS_DARKER)
        if self._hovered:
            return color.lighter(HOVER_LIGHTER)
        return color

    def _caption_width(self) -> int:
        # Reserve the widest caption so swapping text never shifts layout.
        metrics = QFontMetrics(self._font)
        return max(metrics.horizontalAdvance(caption) for caption in self._captions())

    def _text_top(self) -> int:
        # Pull the text up by the leading above its cap height so the visible
        # gap to the glyph equals CAPTION_GAP, not the font's full ascent.
        metrics = QFontMetrics(self._font)
        top_inset = metrics.ascent() - metrics.capHeight()
        return GLYPH_TOP_PADDING + self._style.icon_size + CAPTION_GAP - top_inset

    def sizeHint(self) -> QSize:
        metrics = QFontMetrics(self._font)
        width = max(self._style.icon_size, self._caption_width())
        height = self._text_top() + metrics.height()
        return QSize(width, height)

    def enterEvent(self, event: Any) -> None:
        self._hovered = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event: Any) -> None:
        self._hovered = False
        self.update()
        super().leaveEvent(event)

    def paintEvent(self, event: Any) -> None:
        color = self._state_color()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        glyph = lucide_pixmap(self._style.icon, color.name(), self._style.icon_size)
        glyph_x = (self.width() - self._style.icon_size) // 2
        painter.drawPixmap(glyph_x, GLYPH_TOP_PADDING, glyph)

        painter.setFont(self._font)
        painter.setPen(color)
        text_top = self._text_top()
        text_rect = QRect(0, text_top, self.width(), self.height() - text_top)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop, self._caption())
        painter.end()


@dataclass(frozen=True, slots=True)
class MutableCaptionToolButtonStyle(CaptionToolButtonStyle):
    disabled_color: str = DISABLED_TEXT_COLOR


class MutableCaptionToolButton(CaptionToolButton):
    def __init__(self, style: MutableCaptionToolButtonStyle, parent: QWidget | None = None) -> None:
        super().__init__(style, parent)
        self._style: MutableCaptionToolButtonStyle = style

    def _base_color(self) -> QColor:
        return QColor(self._style.disabled_color if not self.isEnabled() else self._style.color)

    def setEnabled(self, enabled: bool) -> None:
        super().setEnabled(enabled)
        self.update()


@dataclass(frozen=True, slots=True)
class CaptionToolToggleStyle:
    icon: LucideIcon
    checked_caption: str
    unchecked_caption: str
    checked_color: str = palette.ORANGE
    unchecked_color: str = palette.NEUTRAL_3
    icon_size: int = TOOL_ICON_SIZE
    caption_font_size: int = CAPTION_FONT_SIZE


class CaptionedToolToggle(CaptionToolButton):
    def __init__(self, style: CaptionToolToggleStyle, parent: QWidget | None = None) -> None:
        unchecked_style = CaptionToolButtonStyle(
            icon=style.icon,
            caption=style.unchecked_caption,
            color=style.unchecked_color,
            icon_size=style.icon_size,
            caption_font_size=style.caption_font_size,
        )
        super().__init__(unchecked_style, parent)
        self._toggle_style = style
        self.setCheckable(True)

    def _caption(self) -> str:
        return self._toggle_style.checked_caption if self.isChecked() else self._toggle_style.unchecked_caption

    def _base_color(self) -> QColor:
        return QColor(self._toggle_style.checked_color if self.isChecked() else self._toggle_style.unchecked_color)

    def _captions(self) -> tuple[str, ...]:
        return (self._toggle_style.checked_caption, self._toggle_style.unchecked_caption)

    def render_state(self, checked: bool) -> None:
        self.blockSignals(True)
        self.setChecked(checked)
        self.blockSignals(False)
        self.update()
