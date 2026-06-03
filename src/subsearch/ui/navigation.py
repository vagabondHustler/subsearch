from PySide6.QtCore import QPoint, QRect, QRectF, Qt
from PySide6.QtGui import QColor, QCursor, QPainter
from qfluentwidgets import NavigationPanel
from qfluentwidgets.common.color import autoFallbackThemeColor
from qfluentwidgets.common.icon import drawIcon, isDarkTheme

from subsearch.ui.lucide import LucideIcon
from subsearch.ui.typography import TEXT_COLOR

ICON_SIZE = 24
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
        elif (
            (item.isEnter and global_rect.contains(QCursor.pos())) or item.isAboutSelected
        ) and item.isEnabled():
            painter.setBrush(QColor(background, background, background, 6 if item.isAboutSelected else 10))
            painter.drawRoundedRect(item.rect(), 5, 5)

        icon_top = (NAVIGATION_ITEM_HEIGHT - ICON_SIZE) / 2
        icon_rect = QRectF(7.5 + padding_left, icon_top, ICON_SIZE, ICON_SIZE)
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
        items.append(navigation_item.widget.itemWidget)
    for item in items:
        item.paintEvent = lambda event, item=item: _paint_navigation_item_with_large_icon(item, event)
        item.update()
