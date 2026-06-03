from PySide6.QtCore import QSize, Qt, QTimer
from PySide6.QtGui import QColor, QFont, QPainter
from PySide6.QtWidgets import QListWidgetItem, QVBoxLayout, QWidget
from qfluentwidgets import BodyLabel, HeaderCardWidget, ListWidget

from subsearch.logger import log
from subsearch.io import io_file_system, io_toml, string_parser
from subsearch.model import Subtitle
from subsearch.providers import subsource
from subsearch.runtime.constants import FILE_PATHS, VIDEO_FILE
from subsearch.ui.cards import (
    CARD_BORDER_COLOR,
    CARD_BORDER_RADIUS,
    CARD_FILL_COLOR,
    CARD_PANEL_OPACITY,
)
from subsearch.ui.descriptions import SETTING_DESCRIPTIONS
from subsearch.ui.lucide import LucideIcon, lucide_qicon, lucide_rotated_qicon
from subsearch.ui.separators import make_fading_separator
from subsearch.ui.setting_rows import HelpButton
from subsearch.ui.typography import BODY_FONT_SIZE, SEMI_BOLD, apply_body_font, apply_title_font

CARD_BODY_MARGINS = (12, 8, 12, 12)

LIST_FONT_FAMILY = "Segoe UI Semibold"
ICON_SIZE = 16
ROW_HEIGHT = 26

LIST_STYLE_SHEET = """
ListWidget {
    background: transparent;
    border: none;
    outline: none;
}
ListWidget::item {
    background: transparent;
    border: none;
    padding-left: 4px;
}
ListWidget::item:hover,
ListWidget::item:selected {
    background: rgba(255, 255, 255, 18);
    border: none;
    border-radius: 4px;
}
"""

PENDING_COLOR = "#c8c8c7"
DOWNLOADING_COLOR = "#89b4fa"
SUCCESS_COLOR = "#a6d778"
FAILED_COLOR = "#f38ba8"

PENDING_ICON = LucideIcon.CIRCLE
DOWNLOADING_ICON = LucideIcon.CIRCLE_DOT_DASHED
SUCCESS_ICON = LucideIcon.CIRCLE_CHECK_BIG
FAILED_ICON = LucideIcon.CIRCLE_X

SPINNER_FRAME_INTERVAL_MS = 60
SPINNER_DEGREES_PER_FRAME = 10


class SubtitleCard(HeaderCardWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        description = SETTING_DESCRIPTIONS["download_manager.available_subtitles"]
        self.setTitle(description.title)
        apply_title_font(self.headerLabel)
        self._replace_header_separator()
        self._add_header_help(description.explanation)
        self.viewLayout.setContentsMargins(*CARD_BODY_MARGINS)

    def paintEvent(self, e) -> None:
        painter = QPainter(self)
        painter.setRenderHints(QPainter.RenderHint.Antialiasing)
        painter.setOpacity(CARD_PANEL_OPACITY)
        painter.setBrush(CARD_FILL_COLOR)
        painter.setPen(CARD_BORDER_COLOR)
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), CARD_BORDER_RADIUS, CARD_BORDER_RADIUS)

    def _replace_header_separator(self) -> None:
        index = self.vBoxLayout.indexOf(self.separator)
        self.separator.hide()
        self.vBoxLayout.removeWidget(self.separator)
        self.vBoxLayout.insertWidget(index, make_fading_separator())

    def _add_header_help(self, explanation: str) -> None:
        self.headerLayout.addStretch(1)
        self.headerLayout.addWidget(HelpButton(explanation, self))


class DownloadManagerInterface(QWidget):
    def __init__(self, subtitles: list[Subtitle] | None = None) -> None:
        super().__init__()
        self.setObjectName("downloadManagerInterface")
        self.subtitles = sorted(
            subtitles or [], key=lambda subtitle: subtitle.precentage_result, reverse=True
        )
        self.downloaded: list[Subtitle] = []
        self.failed: list[Subtitle] = []
        self.download_number = 1
        self.download_index_size = len(self.subtitles)

        self.spinning_rows: dict[int, tuple[QListWidgetItem, str]] = {}
        self.spinner_angle = 0.0
        self.spinner_timer = QTimer(self)
        self.spinner_timer.setInterval(SPINNER_FRAME_INTERVAL_MS)
        self.spinner_timer.timeout.connect(self._advance_spinner)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(36, 24, 36, 24)
        layout.setSpacing(8)

        card = SubtitleCard(self)
        layout.addWidget(card, stretch=1)

        if not self.subtitles:
            empty_label = BodyLabel("It's very empty...  :(", self)
            apply_body_font(empty_label)
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            card.viewLayout.addWidget(empty_label, stretch=1)
            return

        self.list_widget = ListWidget(self)
        self.list_widget.setStyleSheet(LIST_STYLE_SHEET)
        self.list_widget.setFont(self._list_font())
        self.list_widget.setIconSize(QSize(ICON_SIZE, ICON_SIZE))
        card.viewLayout.addWidget(self.list_widget, stretch=1)
        self.items_by_subtitle: dict[int, Subtitle] = {}
        accept_threshold = io_toml.load_toml_value(FILE_PATHS.config, "search.accept_threshold")
        automatic_downloads = io_toml.load_toml_value(FILE_PATHS.config, "download.automatic")
        for subtitle in self.subtitles:
            item = QListWidgetItem(self._row_text(subtitle))
            item.setFont(self._list_font())
            item.setSizeHint(QSize(0, ROW_HEIGHT))
            item.setIcon(lucide_qicon(PENDING_ICON, PENDING_COLOR))
            item.setForeground(QColor(PENDING_COLOR))
            self.list_widget.addItem(item)
            self.items_by_subtitle[self.list_widget.row(item)] = subtitle
            if subtitle.precentage_result == accept_threshold and not automatic_downloads:
                self.downloaded.append(subtitle)
                self.download_number += 1
                self._set_status(item, subtitle, SUCCESS_ICON, SUCCESS_COLOR)
        self.list_widget.itemClicked.connect(self._on_item_clicked)

    @staticmethod
    def _list_font() -> QFont:
        font = QFont(LIST_FONT_FAMILY)
        font.setPixelSize(BODY_FONT_SIZE)
        font.setWeight(SEMI_BOLD)
        return font

    @staticmethod
    def _row_text(subtitle: Subtitle) -> str:
        return f"{subtitle.precentage_result}%  {subtitle.subtitle_name}"

    def _on_item_clicked(self, item: QListWidgetItem) -> None:
        row = self.list_widget.row(item)
        subtitle = self.items_by_subtitle[row]
        if subtitle in self.downloaded or subtitle in self.failed:
            return
        if subtitle.provider_name == "subsource":
            download_url = subsource.GetDownloadUrl().get_url(subtitle)
            if not download_url:
                self._set_status(item, subtitle, FAILED_ICON, FAILED_COLOR)
                self.failed.append(subtitle)
                return
            subtitle.download_url = download_url
            subtitle.request_data = {}
        self._set_status(item, subtitle, DOWNLOADING_ICON, DOWNLOADING_COLOR)
        self._download(item, subtitle)

    def _download(self, item: QListWidgetItem, subtitle: Subtitle) -> None:
        try:
            if string_parser.valid_filename(subtitle.subtitle_name):
                subtitle.subtitle_name = string_parser.fix_filename(subtitle.subtitle_name)
            io_file_system.download_subtitle(subtitle, self.download_number, self.download_index_size)
            io_file_system.extract_files_in_dir(VIDEO_FILE.tmp_dir, VIDEO_FILE.subs_dir)
            zip_archive = (
                VIDEO_FILE.tmp_dir
                / f"{subtitle.provider_name}_{subtitle.subtitle_name}_{self.download_number}.zip"
            )
            zip_archive.unlink()
            self._set_status(item, subtitle, SUCCESS_ICON, SUCCESS_COLOR)
            self.download_number += 1
            self.download_index_size += 1
            self.downloaded.append(subtitle)
        except Exception as error:
            log.stdout(str(error), level="error")
            self._set_status(item, subtitle, FAILED_ICON, FAILED_COLOR)
            self.failed.append(subtitle)

    def _set_status(
        self, item: QListWidgetItem, subtitle: Subtitle, icon: LucideIcon, color: str
    ) -> None:
        if icon is DOWNLOADING_ICON:
            self._start_spinning(item, color)
        else:
            self._stop_spinning(item)
            item.setIcon(lucide_qicon(icon, color))
        item.setText(self._row_text(subtitle))
        item.setForeground(QColor(color))

    def _start_spinning(self, item: QListWidgetItem, color: str) -> None:
        self.spinning_rows[self.list_widget.row(item)] = (item, color)
        item.setIcon(lucide_rotated_qicon(DOWNLOADING_ICON, color, self.spinner_angle))
        if not self.spinner_timer.isActive():
            self.spinner_timer.start()

    def _stop_spinning(self, item: QListWidgetItem) -> None:
        self.spinning_rows.pop(self.list_widget.row(item), None)
        if not self.spinning_rows:
            self.spinner_timer.stop()

    def _advance_spinner(self) -> None:
        self.spinner_angle = (self.spinner_angle + SPINNER_DEGREES_PER_FRAME) % 360
        for item, color in self.spinning_rows.values():
            item.setIcon(lucide_rotated_qicon(DOWNLOADING_ICON, color, self.spinner_angle))
