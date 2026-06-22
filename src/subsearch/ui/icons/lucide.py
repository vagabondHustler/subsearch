from enum import Enum
from functools import lru_cache
from typing import Any

from PySide6.QtCore import QByteArray, QRectF, QSize, Qt
from PySide6.QtGui import QColor, QIcon, QPainter, QPixmap, QTransform
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtXml import QDomDocument
from qfluentwidgets import FluentIconBase, Theme, getIconColor
from qfluentwidgets.common.icon import SvgIconEngine, drawSvgIcon

from subsearch.ui.icons.icons_data import ICON_SOURCES

STROKE_TAGS = ("path", "circle", "line", "polyline", "polygon", "rect")


@lru_cache(maxsize=None)
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
    FOLDER_SEARCH = "folder-search"
    SETTINGS = "settings"
    CHEVRON_DOWN = "chevron-down"
    CHEVRON_RIGHT = "chevron-right"
    BRAIN = "brain"
    BRAIN_CIRCUIT = "brain-circuit"
    LAYERS_PLUS = "layers-plus"
    LAYERS_MINUS = "layers-minus"
    LIGHTBULB = "lightbulb"
    CIRCLE_CHECK_BIG = "circle-check-big"
    HEART_HANDSHAKE = "heart-handshake"
    CIRCLE = "circle"
    CIRCLE_SMALL = "circle-small"
    CIRCLE_X = "circle-x"
    CIRCLE_DOT_DASHED = "circle-dot-dashed"
    GRIP_HORIZONTAL = "grip-horizontal"
    ARROW_LEFT_RIGHT = "arrow-left-right"
    ARROW_DOWN_TO_LINE = "arrow-down-to-line"
    REFRESH_CW_DOT = "refresh-cw-dot"
    LIST_CHECK = "list-check"
    BUG = "bug"
    BUG_FILE = "bug-file"
    SCROLL_TEXT = "scroll-text"
    EYE = "eye"
    EYE_OFF = "eye-off"
    EXTERNAL_LINK = "external-link"
    GITHUB = "github"
    KEY_ROUND = "key-round"
    SHIELD = "shield"
    TV = "tv"
    MONITOR = "monitor"
    HISTORY = "history"
    SEARCH = "search"
    CAPTIONS = "captions"
    FOLDER_COG = "folder-cog"
    FOLDER_OUTPUT = "folder-output"
    FILE_OUTPUT = "file-output"
    COPY = "copy"
    FILE_ARCHIVE = "file-archive"
    LOGS = "logs"
    FILES = "files"
    FILE_PEN = "file-pen"
    X = "x"
    PICTURE_IN_PICTURE_2 = "picture-in-picture-2"
    SAVE = "save"

    def source(self) -> str:
        return ICON_SOURCES[self.value]

    def path(self, theme: Theme = Theme.AUTO) -> str:
        return self.value

    def icon(self, theme: Theme = Theme.AUTO, color: QColor | None = None) -> QIcon:
        stroke_color = QColor(color).name() if color else getIconColor(theme)
        return QIcon(SvgIconEngine(_recolored_svg(self.source(), stroke_color).decode()))

    def render(self, painter: Any, rect: Any, theme: Any = Theme.AUTO, indexes: Any = None, **attributes: Any) -> None:
        stroke_color = attributes.get("fill") or attributes.get("stroke") or getIconColor(theme)
        drawSvgIcon(QByteArray(_recolored_svg(self.source(), stroke_color)), painter, rect)


@lru_cache(maxsize=None)
def lucide_qicon(icon: LucideIcon, color: str) -> QIcon:
    return icon.icon(color=QColor(color))


@lru_cache(maxsize=None)
def _upright_pixmap(icon: LucideIcon, color: str, size: int) -> QPixmap:
    renderer = QSvgRenderer(QByteArray(_recolored_svg(icon.source(), QColor(color).name())))
    pixmap = QPixmap(QSize(size, size))
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    renderer.render(painter, QRectF(0, 0, size, size))
    painter.end()
    return pixmap


@lru_cache(maxsize=None)
def lucide_rotated_qicon(icon: LucideIcon, color: str, angle: float, size: int = 32) -> QIcon:
    rotated = _upright_pixmap(icon, color, size).transformed(
        QTransform().rotate(angle), Qt.TransformationMode.SmoothTransformation
    )
    return QIcon(rotated)
