from enum import Enum

from PySide6.QtCore import QRectF, QSize, Qt
from PySide6.QtGui import QColor, QIcon, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtXml import QDomDocument
from qfluentwidgets import FluentIconBase, Theme, getIconColor
from qfluentwidgets.common.icon import SvgIconEngine, drawSvgIcon

from subsearch.ui.icons_data import ICON_SOURCES

STROKE_TAGS = ("path", "circle", "line", "polyline", "polygon", "rect")


def _recolored_svg(svg_source: str, color: str) -> bytes:
    dom = QDomDocument()
    dom.setContent(svg_source)
    root = dom.documentElement()
    root.setAttribute("stroke", color)
    for tag in STROKE_TAGS:
        nodes = dom.elementsByTagName(tag)
        for index in range(nodes.length()):
            nodes.at(index).toElement().setAttribute("stroke", color)
    return dom.toString().encode()


class LucideIcon(FluentIconBase, Enum):
    TEXT_SEARCH = "text-search"
    MONITOR_COG = "monitor-cog"
    FOLDER_DOWN = "folder-down"
    FOLDER_OPEN = "folder-open"
    SETTINGS = "settings"
    LIGHTBULB = "lightbulb"
    CIRCLE_CHECK_BIG = "circle-check-big"
    HEART_HANDSHAKE = "heart-handshake"
    PACKAGE_SEARCH = "package-search"
    PACKAGE_OPEN = "package-open"
    CIRCLE = "circle"
    CIRCLE_X = "circle-x"
    CIRCLE_DOT_DASHED = "circle-dot-dashed"

    def source(self) -> str:
        return ICON_SOURCES[self.value]

    def path(self, theme: Theme = Theme.AUTO) -> str:
        return self.value

    def icon(self, theme: Theme = Theme.AUTO, color: QColor | None = None) -> QIcon:
        stroke_color = QColor(color).name() if color else getIconColor(theme)
        return QIcon(SvgIconEngine(_recolored_svg(self.source(), stroke_color).decode()))

    def render(self, painter, rect, theme=Theme.AUTO, indexes=None, **attributes) -> None:
        stroke_color = attributes.get("fill") or attributes.get("stroke") or getIconColor(theme)
        drawSvgIcon(_recolored_svg(self.source(), stroke_color), painter, rect)


def lucide_qicon(icon: LucideIcon, color: str) -> QIcon:
    return icon.icon(color=QColor(color))


def lucide_rotated_qicon(icon: LucideIcon, color: str, angle: float, size: int = 32) -> QIcon:
    renderer = QSvgRenderer(_recolored_svg(icon.source(), QColor(color).name()))
    pixmap = QPixmap(QSize(size, size))
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    center = size / 2
    painter.translate(center, center)
    painter.rotate(angle)
    painter.translate(-center, -center)
    renderer.render(painter, QRectF(0, 0, size, size))
    painter.end()
    return QIcon(pixmap)
