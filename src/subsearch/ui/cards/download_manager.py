from PySide6.QtCore import QSize, Qt, QTimer
from PySide6.QtGui import QColor, QFont, QPainter
from PySide6.QtWidgets import QListWidgetItem, QVBoxLayout, QWidget
from qfluentwidgets import BodyLabel, HeaderCardWidget, ListWidget

from subsearch.runtime.models.model import (
    MatchTier,
    Subtitle,
    SubtitleStatus,
    classify_match_tier,
)
from subsearch.ui.cards import (
    CARD_BORDER_COLOR,
    CARD_BORDER_RADIUS,
    CARD_FILL_COLOR,
    CARD_PANEL_OPACITY,
)
from subsearch.ui.cards.descriptions import SETTING_DESCRIPTIONS
from subsearch.ui.icons.lucide import LucideIcon, lucide_qicon, lucide_rotated_qicon
from subsearch.ui.services.subtitle_downloads import SubtitleDownloadService
from subsearch.ui.state.store import SettingsStore
from subsearch.ui.theme import palette
from subsearch.ui.theme.separators import make_fading_separator
from subsearch.ui.theme.typography import (
    BODY_FONT_SIZE,
    SEMI_BOLD,
    apply_body_font,
    apply_title_font,
)
from subsearch.ui.widgets.setting_rows import HelpButton

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

PENDING_COLOR = palette.NEUTRAL_1
DOWNLOADING_COLOR = palette.BLUE
SUCCESS_COLOR = palette.GREEN
FAILED_COLOR = palette.RED

PENDING_ICON = LucideIcon.CIRCLE
DOWNLOADING_ICON = LucideIcon.CIRCLE_DOT_DASHED
SUCCESS_ICON = LucideIcon.CIRCLE_CHECK_BIG
FAILED_ICON = LucideIcon.CIRCLE_X

SPINNER_FRAME_INTERVAL_MS = 60
SPINNER_DEGREES_PER_FRAME = 10


class SubtitleCard(HeaderCardWidget):
    def __init__(self, parent: QWidget | None = None) -> None:  # pyright: ignore[reportIncompatibleVariableOverride]
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
    def __init__(
        self,
        store: SettingsStore,
        download_service: SubtitleDownloadService,
        subtitles: list[Subtitle] | None = None,
    ) -> None:
        super().__init__()
        self.setObjectName("downloadManagerInterface")
        self.accept_threshold = store.read("search.accept_threshold")
        self.download_service = download_service
        self.subtitles = sorted(subtitles or [], key=self._sort_key, reverse=True)
        self.downloaded: list[Subtitle] = []
        self.failed: list[Subtitle] = []

        self.items_by_subtitle_id: dict[int, QListWidgetItem] = {}
        self.subtitles_by_row: dict[int, Subtitle] = {}
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

        self.download_service.set_download_total(len(self.subtitles))
        self.download_service.started.connect(self._on_download_started)
        self.download_service.succeeded.connect(self._on_download_succeeded)
        self.download_service.failed.connect(self._on_download_failed)

        self.list_widget = ListWidget(self)
        self.list_widget.setStyleSheet(LIST_STYLE_SHEET)
        self.list_widget.setFont(self._list_font())
        self.list_widget.setIconSize(QSize(ICON_SIZE, ICON_SIZE))
        card.viewLayout.addWidget(self.list_widget, stretch=1)
        for subtitle in self.subtitles:
            item = QListWidgetItem(self._row_text(subtitle))
            item.setFont(self._list_font())
            item.setSizeHint(QSize(0, ROW_HEIGHT))
            item.setIcon(lucide_qicon(PENDING_ICON, PENDING_COLOR))
            item.setForeground(QColor(PENDING_COLOR))
            self.list_widget.addItem(item)
            self.items_by_subtitle_id[id(subtitle)] = item
            self.subtitles_by_row[self.list_widget.row(item)] = subtitle
            if subtitle.status is SubtitleStatus.AUTO_DOWNLOADED:
                self.downloaded.append(subtitle)
                self._render_status(item, subtitle, SUCCESS_ICON, SUCCESS_COLOR)
        self.list_widget.itemClicked.connect(self._on_item_clicked)

        self._enqueue_accepted_subtitles()

    @staticmethod
    def _list_font() -> QFont:
        font = QFont(LIST_FONT_FAMILY)
        font.setPixelSize(BODY_FONT_SIZE)
        font.setWeight(SEMI_BOLD)
        return font

    def _match_tier(self, subtitle: Subtitle) -> MatchTier:
        return classify_match_tier(subtitle.hash_match, subtitle.token_result, self.accept_threshold)

    def _sort_key(self, subtitle: Subtitle) -> tuple[int, int]:
        return self._match_tier(subtitle), subtitle.token_result

    def _row_text(self, subtitle: Subtitle) -> str:
        tier = self._match_tier(subtitle)
        return f"[{tier.name}] {subtitle.token_result}%  {subtitle.subtitle_name}"

    def _enqueue_accepted_subtitles(self) -> None:
        for subtitle in self.subtitles:
            if subtitle.status is SubtitleStatus.ACCEPTED and subtitle.download_url:
                self.download_service.enqueue(subtitle)

    def _on_item_clicked(self, item: QListWidgetItem) -> None:
        subtitle = self.subtitles_by_row[self.list_widget.row(item)]
        if subtitle in self.downloaded or subtitle in self.failed:
            return
        if not subtitle.download_url:
            subtitle.status = SubtitleStatus.DOWNLOAD_FAILED
            self.failed.append(subtitle)
            self._render_status(item, subtitle, FAILED_ICON, FAILED_COLOR)
            return
        self.download_service.enqueue(subtitle)

    def _item_for(self, subtitle: Subtitle) -> QListWidgetItem | None:
        return self.items_by_subtitle_id.get(id(subtitle))

    def _on_download_started(self, subtitle: Subtitle) -> None:
        item = self._item_for(subtitle)
        if item is not None:
            self._render_status(item, subtitle, DOWNLOADING_ICON, DOWNLOADING_COLOR)

    def _on_download_succeeded(self, subtitle: Subtitle) -> None:
        self.downloaded.append(subtitle)
        item = self._item_for(subtitle)
        if item is not None:
            self._render_status(item, subtitle, SUCCESS_ICON, SUCCESS_COLOR)

    def _on_download_failed(self, subtitle: Subtitle, _message: str) -> None:
        self.failed.append(subtitle)
        item = self._item_for(subtitle)
        if item is not None:
            self._render_status(item, subtitle, FAILED_ICON, FAILED_COLOR)

    def _render_status(self, item: QListWidgetItem, subtitle: Subtitle, icon: LucideIcon, color: str) -> None:
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
