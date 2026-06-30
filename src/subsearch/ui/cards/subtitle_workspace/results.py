from pathlib import Path

from PySide6.QtCore import QEvent, QObject, QPoint, QSize, Qt, QTimer, Signal
from PySide6.QtGui import (
    QColor,
    QDragEnterEvent,
    QDropEvent,
    QFont,
    QIcon,
    QMouseEvent,
)
from PySide6.QtWidgets import QListWidgetItem, QVBoxLayout, QWidget
from qfluentwidgets import BodyLabel, ListWidget

from subsearch.runtime.config import SEARCH_SUBJECT, SUPPORTED_FILE_EXT
from subsearch.runtime.config.defaults import ConfigKey
from subsearch.runtime.models import (
    MatchTier,
    Subtitle,
    SubtitleStatus,
    classify_match_tier,
)
from subsearch.ui.cards.subtitle_workspace._constants import (
    DOWNLOADING_COLOR,
    DOWNLOADING_ICON,
    FAILED_COLOR,
    FAILED_ICON,
    ICON_SIZE,
    IDLE_PLACEHOLDER_TEXT,
    LIST_FONT_FAMILY,
    LIST_STYLE_SHEET,
    NO_RESULTS_PLACEHOLDER_TEXT,
    PENDING_COLOR,
    PENDING_ICON,
    ROW_HEIGHT,
    SEARCHING_PLACEHOLDER_TEXT,
    SUCCESS_COLOR,
    SUCCESS_ICON,
)
from subsearch.ui.cards.subtitle_workspace.action_row import SubtitleActionRow
from subsearch.ui.cards.subtitle_workspace.card import SubtitleCard
from subsearch.ui.cards.subtitle_workspace.search_bar import SubtitleSearchBar
from subsearch.ui.cards.subtitle_workspace.splitter import _build_splitter
from subsearch.ui.compat.qfluent import (
    inset_list_highlight_right,
    set_list_hovered_row,
)
from subsearch.ui.icons.lucide import LucideIcon, lucide_qicon
from subsearch.ui.services.console_view import ConsoleViewSink
from subsearch.ui.services.post_processing import PostProcessingServiceProtocol
from subsearch.ui.services.season_episode_suggestions import (
    SeasonEpisodeSuggestionService,
)
from subsearch.ui.services.subtitle_downloads import DownloadServiceProtocol
from subsearch.ui.services.title_suggestions import TitleSuggestionService
from subsearch.ui.services.video_file import VideoFileService
from subsearch.ui.state.store import SettingsStore
from subsearch.ui.theme.metrics import LIST_SCROLLBAR_WIDTH
from subsearch.ui.theme.typography import (
    BODY_FONT_SIZE,
    SEMI_BOLD,
    TEXT_COLOR,
    apply_body_font,
)
from subsearch.ui.widgets.console_view import ConsoleView
from subsearch.ui.widgets.context_menu_popup import ContextMenuItem, ContextMenuPopup
from subsearch.ui.widgets.ripple_spinner import (
    CYCLE_MS,
    FRAME_INTERVAL_MS,
    ripple_pixmap,
)


class ManualSearchInterface(QWidget):
    research_requested = Signal(str, object)

    def __init__(
        self,
        store: SettingsStore,
        download_service: DownloadServiceProtocol,
        post_processing_service: PostProcessingServiceProtocol,
        video_file_service: VideoFileService,
        subtitles: list[Subtitle] | None = None,
        console_view_sink: ConsoleViewSink | None = None,
        title_suggestion_service: TitleSuggestionService | None = None,
        season_episode_suggestion_service: SeasonEpisodeSuggestionService | None = None,
    ) -> None:
        super().__init__()
        self.setObjectName("manualSearchInterface")
        self.setAcceptDrops(True)
        self._store = store
        self._post_processing_service = post_processing_service
        self.accept_threshold = store.read(ConfigKey.SEARCH_ACCEPT_THRESHOLD)
        self.download_service = download_service
        self.subtitles = sorted(subtitles or [], key=self._sort_key, reverse=True)
        self.skipped_providers: list[str] = []
        self.downloaded: list[Subtitle] = []
        self.failed: list[Subtitle] = []
        self.placed_best_next_to_video = False

        self.items_by_subtitle_id: dict[int, QListWidgetItem] = {}
        self.action_rows_by_subtitle_id: dict[int, SubtitleActionRow] = {}
        self.subtitles_by_row: dict[int, Subtitle] = {}
        self.spinning_rows: dict[int, tuple[QListWidgetItem, str]] = {}
        self.spinner_progress = 0.0
        self.spinner_timer = QTimer(self)
        self.spinner_timer.setInterval(FRAME_INTERVAL_MS)
        self.spinner_timer.timeout.connect(self._advance_spinner)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(36, 24, 36, 24)
        layout.setSpacing(8)

        self._search_bar = SubtitleSearchBar(
            store, video_file_service, title_suggestion_service, season_episode_suggestion_service, self
        )
        self._search_bar.research_requested.connect(self.research_requested)
        layout.addWidget(self._search_bar)

        self._card = SubtitleCard(self)
        self._card.search_text_changed.connect(self._filter_list)
        self._card.search_confirmed.connect(self._select_first_visible)

        if console_view_sink is not None:
            self._console_view = ConsoleView(console_view_sink, self)
            self._splitter = _build_splitter(self._card, self._console_view)
            layout.addWidget(self._splitter, stretch=1)
        else:
            layout.addWidget(self._card, stretch=1)

        if not self.subtitles:
            self._show_placeholder(IDLE_PLACEHOLDER_TEXT)
            return

        self._build_list_widget()

    def _show_placeholder(self, text: str) -> None:
        self._empty_label = BodyLabel(text, self)
        apply_body_font(self._empty_label)
        self._empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._card.viewLayout.addWidget(self._empty_label, stretch=1)

    def _clear_placeholder(self) -> None:
        empty_label = getattr(self, "_empty_label", None)
        if empty_label is not None:
            empty_label.deleteLater()
            del self._empty_label

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if self._dropped_video_file(event) is not None:
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent) -> None:
        video_file = self._dropped_video_file(event)
        if video_file is None:
            event.ignore()
            return
        event.acceptProposedAction()
        self._search_bar.select_dropped_video(video_file)
        self.research_requested.emit("", None)

    @staticmethod
    def _dropped_video_file(event: QDragEnterEvent | QDropEvent) -> Path | None:
        mime_data = event.mimeData()
        if not mime_data.hasUrls():
            return None
        urls = [url for url in mime_data.urls() if url.isLocalFile()]
        if len(urls) != 1:
            return None
        path = Path(urls[0].toLocalFile())
        if path.suffix.lstrip(".").lower() not in SUPPORTED_FILE_EXT:
            return None
        return path

    def reset_for_search(self) -> None:
        self._search_bar.start_spinner()
        self._disconnect_download_service()
        self._teardown_list_widget()
        self._clear_placeholder()
        self.subtitles = []
        self.skipped_providers = []
        self.downloaded = []
        self.failed = []
        self.placed_best_next_to_video = False
        self.items_by_subtitle_id.clear()
        self.action_rows_by_subtitle_id.clear()
        self.subtitles_by_row.clear()
        self._show_placeholder(SEARCHING_PLACEHOLDER_TEXT)

    def _disconnect_download_service(self) -> None:
        for signal in (self.download_service.started, self.download_service.succeeded, self.download_service.failed):
            try:
                signal.disconnect(self)
            except RuntimeError, TypeError:
                pass

    def _teardown_list_widget(self) -> None:
        list_widget = getattr(self, "list_widget", None)
        if list_widget is not None:
            list_widget.deleteLater()
            del self.list_widget
        self.spinner_timer.stop()
        self.spinning_rows.clear()

    def populate(self, subtitles: list[Subtitle], skipped_providers: list[str] | None = None) -> None:
        self._search_bar.stop_spinner()
        self.accept_threshold = self._store.read(ConfigKey.SEARCH_ACCEPT_THRESHOLD)
        self.subtitles = sorted(subtitles, key=self._sort_key, reverse=True)
        self.skipped_providers = skipped_providers or []
        self._clear_placeholder()
        self._build_list_widget()

    def _no_results_text(self) -> str:
        return "\n".join([NO_RESULTS_PLACEHOLDER_TEXT, *self.skipped_providers])

    def _build_list_widget(self) -> None:
        if not self.subtitles:
            self._show_placeholder(self._no_results_text())
            return

        self.download_service.set_download_total(len(self.subtitles))
        self.download_service.started.connect(self._on_download_started)
        self.download_service.succeeded.connect(self._on_download_succeeded)
        self.download_service.failed.connect(self._on_download_failed)

        self.list_widget = ListWidget(self)
        self.list_widget.setStyleSheet(LIST_STYLE_SHEET)
        inset_list_highlight_right(self.list_widget, LIST_SCROLLBAR_WIDTH)
        self.list_widget.setFont(self._list_font())
        self.list_widget.setIconSize(QSize(ICON_SIZE, ICON_SIZE))
        viewport = self.list_widget.viewport()
        viewport.setMouseTracking(True)
        viewport.installEventFilter(self)
        self.list_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.list_widget.customContextMenuRequested.connect(self._open_context_menu)
        self._card.viewLayout.addWidget(self.list_widget, stretch=1)
        for subtitle in self.subtitles:
            item = QListWidgetItem(self._row_text(subtitle))
            item.setFont(self._list_font())
            item.setSizeHint(QSize(0, ROW_HEIGHT))
            item.setIcon(lucide_qicon(PENDING_ICON, PENDING_COLOR))
            item.setForeground(QColor(PENDING_COLOR))
            self.list_widget.addItem(item)
            self.items_by_subtitle_id[id(subtitle)] = item
            self.subtitles_by_row[self.list_widget.row(item)] = subtitle
            if subtitle.status is SubtitleStatus.AUTO_DOWNLOAD:
                self.downloaded.append(subtitle)
                self._render_status(item, subtitle, SUCCESS_ICON, SUCCESS_COLOR)
                self._attach_action_buttons(item, subtitle)
        self.list_widget.itemDoubleClicked.connect(self._on_item_clicked)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        list_widget = getattr(self, "list_widget", None)
        if (
            list_widget is not None
            and watched is list_widget.viewport()
            and isinstance(event, QMouseEvent)
            and event.type() == QEvent.Type.MouseMove
        ):
            self._sync_hovered_row(list_widget, event.position().toPoint())
        return super().eventFilter(watched, event)

    @staticmethod
    def _sync_hovered_row(list_widget: ListWidget, viewport_position: QPoint) -> None:
        set_list_hovered_row(list_widget, list_widget.indexAt(viewport_position).row())

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
        return f"{subtitle.token_result}%  {subtitle.subtitle_name}"

    def _filter_list(self, query: str) -> None:
        if not hasattr(self, "list_widget"):
            return
        lowered = query.lower()
        for row, subtitle in self.subtitles_by_row.items():
            item = self.list_widget.item(row)
            if item is not None:
                item.setHidden(bool(lowered) and lowered not in subtitle.subtitle_name.lower())

    def _select_first_visible(self) -> None:
        if not hasattr(self, "list_widget"):
            return
        for row in range(self.list_widget.count()):
            item = self.list_widget.item(row)
            if item is not None and not item.isHidden():
                self.list_widget.setCurrentItem(item)
                self.list_widget.scrollToItem(item)
                break

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

    def _open_context_menu(self, position: QPoint) -> None:
        item = self.list_widget.itemAt(position)
        if item is None:
            return
        subtitle = self.subtitles_by_row[self.list_widget.row(item)]
        menu = ContextMenuPopup(self, self._context_menu_items(subtitle))
        menu.show_at_point(self.list_widget.viewport().mapToGlobal(position))

    def _context_menu_items(self, subtitle: Subtitle) -> list[ContextMenuItem]:
        already_downloaded = subtitle in self.downloaded
        action_row = self.action_rows_by_subtitle_id.get(id(subtitle))
        return [
            ContextMenuItem(
                LucideIcon.ARROW_DOWN_TO_LINE,
                "Download subtitle",
                lambda: self._on_item_clicked(self.items_by_subtitle_id[id(subtitle)]),
                enabled=not already_downloaded and bool(subtitle.download_url),
            ),
            ContextMenuItem(
                LucideIcon.FILES,
                "Move to extraction folder",
                lambda: action_row.trigger_move() if action_row else None,
                enabled=action_row is not None,
            ),
            ContextMenuItem(
                LucideIcon.FILE_PEN,
                "Unpack, rename and place next to video",
                lambda: action_row.trigger_rename_and_place() if action_row else None,
                enabled=action_row is not None and SEARCH_SUBJECT.file_exists,
            ),
            ContextMenuItem(
                LucideIcon.FOLDER_SEARCH,
                "Open containing folder",
                lambda: action_row.trigger_open_location() if action_row else None,
                enabled=action_row is not None and action_row.has_delivered_directory(),
            ),
        ]

    def _item_for(self, subtitle: Subtitle) -> QListWidgetItem | None:
        return self.items_by_subtitle_id.get(id(subtitle))

    def _attach_action_buttons(self, item: QListWidgetItem, subtitle: Subtitle) -> None:
        row = SubtitleActionRow(
            subtitle,
            self._store,
            self._post_processing_service,
            self.list_widget,
        )
        self.list_widget.setItemWidget(item, row)
        self.action_rows_by_subtitle_id[id(subtitle)] = row

    def _on_download_started(self, subtitle: Subtitle) -> None:
        item = self._item_for(subtitle)
        if item is not None:
            self._render_status(item, subtitle, DOWNLOADING_ICON, DOWNLOADING_COLOR)

    def _on_download_succeeded(self, subtitle: Subtitle) -> None:
        self.downloaded.append(subtitle)
        item = self._item_for(subtitle)
        if item is not None:
            self._render_status(item, subtitle, SUCCESS_ICON, SUCCESS_COLOR)
            self._attach_action_buttons(item, subtitle)
            self._auto_post_process(subtitle)

    def _auto_post_process(self, subtitle: Subtitle) -> None:
        action_row = self.action_rows_by_subtitle_id.get(id(subtitle))
        if action_row is None:
            return
        action_row.trigger_automatic_post_processing()
        if SEARCH_SUBJECT.file_exists:
            self.placed_best_next_to_video = True

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
        # Only the status icon carries the state color; the row text stays neutral.
        item.setForeground(QColor(TEXT_COLOR))

    def _start_spinning(self, item: QListWidgetItem, color: str) -> None:
        self.spinning_rows[self.list_widget.row(item)] = (item, color)
        item.setIcon(QIcon(ripple_pixmap(ICON_SIZE, color, self.spinner_progress)))
        if not self.spinner_timer.isActive():
            self.spinner_timer.start()

    def _stop_spinning(self, item: QListWidgetItem) -> None:
        self.spinning_rows.pop(self.list_widget.row(item), None)
        if not self.spinning_rows:
            self.spinner_timer.stop()

    def _advance_spinner(self) -> None:
        self.spinner_progress = (self.spinner_progress + FRAME_INTERVAL_MS / CYCLE_MS) % 1.0
        for item, color in self.spinning_rows.values():
            item.setIcon(QIcon(ripple_pixmap(ICON_SIZE, color, self.spinner_progress)))
