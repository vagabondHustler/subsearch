from PySide6.QtCore import QPoint, QRect, QRectF, Qt
from PySide6.QtGui import QColor, QCursor, QPainter
from qfluentwidgets import NavigationPanel
from qfluentwidgets.common.color import autoFallbackThemeColor
from qfluentwidgets.common.icon import drawIcon, isDarkTheme
from qfluentwidgets.components.navigation.navigation_widget import NavigationPushButton

from subsearch.ui.icons.lucide import LucideIcon
from subsearch.ui.theme.typography import TEXT_COLOR

ICON_SIZE = 24
NAVIGATION_ITEM_HEIGHT = 36


class LargeIconNavigationItemMixin(NavigationPushButton):
    def paintEvent(self, e) -> None:
        painter = QPainter(self)
        try:
            painter.setRenderHints(
                QPainter.RenderHint.Antialiasing
                | QPainter.RenderHint.TextAntialiasing
                | QPainter.RenderHint.SmoothPixmapTransform
            )
            painter.setPen(Qt.PenStyle.NoPen)

            if self.isPressed:
                painter.setOpacity(0.7)
            if not self.isEnabled():
                painter.setOpacity(0.4)

            background = 255 if isDarkTheme() else 0
            margins = self._margins()
            padding_left, padding_right = margins.left(), margins.right()
            global_rect = QRect(self.mapToGlobal(QPoint()), self.size())

            if self._canDrawIndicator():
                painter.setBrush(QColor(background, background, background, 6 if self.isEnter else 10))
                painter.drawRoundedRect(self.rect(), 5, 5)
                painter.setBrush(autoFallbackThemeColor(self.lightIndicatorColor, self.darkIndicatorColor))
                painter.drawRoundedRect(self.indicatorRect(), 1.5, 1.5)
            elif (
                (self.isEnter and global_rect.contains(QCursor.pos())) or self.isAboutSelected
            ) and self.isEnabled():
                painter.setBrush(QColor(background, background, background, 6 if self.isAboutSelected else 10))
                painter.drawRoundedRect(self.rect(), 5, 5)

            icon_top = (NAVIGATION_ITEM_HEIGHT - ICON_SIZE) / 2
            icon_rect = QRectF(7.5 + padding_left, icon_top, ICON_SIZE, ICON_SIZE)
            if isinstance(self._icon, LucideIcon):
                self._icon.render(painter, icon_rect, stroke=TEXT_COLOR)
            else:
                drawIcon(self._icon, painter, icon_rect)

            if self.isCompacted:
                return

            painter.setFont(self.font())
            painter.setPen(self.textColor())
            text_left = 44 + padding_left if not self.icon().isNull() else padding_left + 16
            painter.drawText(
                QRectF(text_left, 0, self.width() - 13 - text_left - padding_right, self.height()),
                Qt.AlignmentFlag.AlignVCenter,
                self.text(),
            )
        finally:
            painter.end()


_large_icon_subclass_cache: dict[type, type] = {}


def _large_icon_subclass(item_class: type) -> type:
    if item_class not in _large_icon_subclass_cache:
        _large_icon_subclass_cache[item_class] = type(
            f"LargeIcon{item_class.__name__}", (LargeIconNavigationItemMixin, item_class), {}
        )
    return _large_icon_subclass_cache[item_class]


def enlarge_navigation_icons(panel: NavigationPanel) -> None:
    items = [panel.menuButton, panel.returnButton]
    for navigation_item in panel.items.values():
        items.append(getattr(navigation_item.widget, "itemWidget"))
    for item in items:
        item.__class__ = _large_icon_subclass(type(item))
        item.update()
