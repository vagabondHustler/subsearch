from pathlib import Path

from PySide6.QtCore import QByteArray, QRect, QSize, Qt, QTimer, QUrl, Signal
from PySide6.QtGui import (
    QColor,
    QDesktopServices,
    QDragEnterEvent,
    QDropEvent,
    QFont,
    QIcon,
    QPainter,
    QPen,
)
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import (
    QHBoxLayout,
    QListWidgetItem,
    QSplitter,
    QSplitterHandle,
    QVBoxLayout,
    QWidget,
)
from qfluentwidgets import BodyLabel, LineEdit, ListWidget, TransparentToolButton

from subsearch.parsing.imdb_lookup import (
    EpisodeSuggestion,
    SeasonSuggestion,
    TitleSuggestion,
)
from subsearch.parsing.release_parser import get_release_info
from subsearch.runtime.config import SEARCH_SUBJECT, SUPPORTED_FILE_EXT, WORKSPACE
from subsearch.runtime.config.defaults import ConfigKey
from subsearch.runtime.models import (
    MatchTier,
    Subtitle,
    SubtitleStatus,
    classify_match_tier,
)
from subsearch.ui.cards.base import SettingsCard
from subsearch.ui.cards.descriptions import SETTING_DESCRIPTIONS, CardKey
from subsearch.ui.compat.qfluent import flatten_line_edit, inset_list_highlight_right
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
from subsearch.ui.theme import palette
from subsearch.ui.theme.metrics import (
    LIST_SCROLLBAR_WIDTH,
    ROW_INSET,
    SMALL_ICON_SIZE,
    TOOL_BUTTON_SIZE,
)
from subsearch.ui.theme.separators import SEPARATOR_INSET
from subsearch.ui.theme.typography import (
    BODY_FONT_SIZE,
    SEMI_BOLD,
    TEXT_COLOR,
    apply_body_font,
)
from subsearch.ui.widgets.console_view import ConsoleView
from subsearch.ui.widgets.icon_caption_button import CaptionedToolButton
from subsearch.ui.widgets.ripple_spinner import (
    CYCLE_MS,
    FRAME_INTERVAL_MS,
    ripple_pixmap,
)
from subsearch.ui.widgets.row_icon_button import RowIconButton
from subsearch.ui.widgets.search_line_edit import SearchLineEdit
from subsearch.ui.widgets.suggestion_popup import (
    NumberSuggestionPopup,
    TitleSuggestionPopup,
)

CARD_BODY_MARGINS = (12, 8, 12, 12)

_LOG_DEFAULT_VISIBLE_LINES = 4

_HANDLE_HEIGHT = 20
_HANDLE_LINE_WIDTH_FRACTION = 0.75
_ICON_SIZE = 16


class _SplitterHandle(QSplitterHandle):
    def __init__(self, orientation: Qt.Orientation, parent: QSplitter) -> None:
        super().__init__(orientation, parent)
        self.setCursor(Qt.CursorShape.SizeVerCursor)
        svg_bytes = LucideIcon.GRIP_HORIZONTAL.source().encode()
        self._normal_svg = self._recolor(svg_bytes, palette.POPUP_BORDER)
        self._hover_svg = self._recolor(svg_bytes, palette.NEUTRAL_3)
        self._hovered = False

    @staticmethod
    def _recolor(svg_bytes: bytes, color: str) -> bytes:
        return svg_bytes.replace(b"currentColor", color.encode())

    def sizeHint(self) -> QSize:
        return QSize(0, _HANDLE_HEIGHT)

    def enterEvent(self, _event) -> None:
        self._hovered = True
        self.update()

    def leaveEvent(self, _event) -> None:
        self._hovered = False
        self.update()

    def paintEvent(self, _event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        line_color = palette.NEUTRAL_3 if self._hovered else palette.POPUP_BORDER
        pen = QPen(QColor(line_color), 1)
        painter.setPen(pen)
        mid_y = self.height() // 2
        line_width = int(self.width() * _HANDLE_LINE_WIDTH_FRACTION)
        line_x = (self.width() - line_width) // 2
        icon_gap = _ICON_SIZE // 2 + 4
        center_x = self.width() // 2
        painter.drawLine(line_x, mid_y, center_x - icon_gap, mid_y)
        painter.drawLine(center_x + icon_gap, mid_y, line_x + line_width, mid_y)

        svg_data = self._hover_svg if self._hovered else self._normal_svg
        renderer = QSvgRenderer(QByteArray(svg_data))
        icon_rect = QRect(
            (self.width() - _ICON_SIZE) // 2,
            (self.height() - _ICON_SIZE) // 2,
            _ICON_SIZE,
            _ICON_SIZE,
        )
        renderer.render(painter, icon_rect)
        painter.end()


class _StyledSplitter(QSplitter):
    def createHandle(self) -> QSplitterHandle:
        return _SplitterHandle(self.orientation(), self)


def _build_splitter(top: QWidget, bottom: ConsoleView) -> QSplitter:
    splitter = _StyledSplitter(Qt.Orientation.Vertical)
    splitter.setChildrenCollapsible(False)
    splitter.addWidget(top)
    splitter.addWidget(bottom)
    top.setMinimumHeight(80)
    default_height = bottom.height_for_lines(_LOG_DEFAULT_VISIBLE_LINES)
    bottom.setMinimumHeight(default_height)
    splitter.setSizes([splitter.sizeHint().height() - default_height, default_height])
    splitter.setStretchFactor(0, 1)
    splitter.setStretchFactor(1, 0)
    return splitter


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

# The two trailing action icons sit tight together as one control group; the
# rightmost one is inset by ROW_INSET so it lines up with the card header's lamp.
ACTION_BUTTON_GAP = 0

PENDING_COLOR = palette.NEUTRAL_1
DOWNLOADING_COLOR = palette.BLUE
SUCCESS_COLOR = palette.GREEN
FAILED_COLOR = palette.RED

PENDING_ICON = LucideIcon.CIRCLE
# Sentinel marking the downloading state; rendered as the ripple animation, not this icon.
DOWNLOADING_ICON = LucideIcon.CIRCLE_DOT_DASHED
SUCCESS_ICON = LucideIcon.CIRCLE_CHECK_BIG
FAILED_ICON = LucideIcon.CIRCLE_X

FILTER_BAR_WIDTH = 200

# Match the splitter handle's centered line (_HANDLE_LINE_WIDTH_FRACTION) so the
# search field and the separator below it span the same width.
SEARCH_BAR_WIDTH_FRACTION = _HANDLE_LINE_WIDTH_FRACTION

IDLE_PLACEHOLDER_TEXT = "Drag and drop a video, or or use the search bar"
SEARCHING_PLACEHOLDER_TEXT = "Searching for subtitles…"
NO_RESULTS_PLACEHOLDER_TEXT = "No subtitles found"


class SubtitleSearchBar(QWidget):
    research_requested = Signal(str, object)

    def __init__(
        self,
        store: SettingsStore,
        video_file_service: VideoFileService,
        title_suggestion_service: TitleSuggestionService | None = None,
        season_episode_suggestion_service: SeasonEpisodeSuggestionService | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.store = store
        self._video_file_service = video_file_service
        self._title_suggestion_service = title_suggestion_service
        self._season_episode_suggestion_service = season_episode_suggestion_service
        self._awaiting_suggestions = False
        self._term_without_suggestions = ""
        self._committed_filename = SEARCH_SUBJECT.name if SEARCH_SUBJECT.file_exists else ""
        self._pending_series: TitleSuggestion | None = None
        self._pending_season = 0
        if title_suggestion_service is not None:
            title_suggestion_service.suggestions_ready.connect(self._on_suggestions_ready)
            title_suggestion_service.lookup_failed.connect(self._on_suggestion_lookup_failed)
        if season_episode_suggestion_service is not None:
            season_episode_suggestion_service.seasons_ready.connect(self._on_seasons_ready)
            season_episode_suggestion_service.episodes_ready.connect(self._on_episodes_ready)
            season_episode_suggestion_service.lookup_failed.connect(self._on_season_episode_lookup_failed)

        self._build_video_file_section()
        store.subscribe(ConfigKey.SEARCH_PROVIDERS, self._on_providers_changed)
        self._on_providers_changed(store.read(ConfigKey.SEARCH_PROVIDERS))

    def _on_providers_changed(self, providers: dict) -> None:
        all_disabled = not any(providers.values())
        self._filename_edit.set_button_enabled(not all_disabled)
        if all_disabled:
            self._filename_edit.set_button_tooltip("Enable at least one subtitle provider to search")
        else:
            self._filename_edit.set_button_tooltip("Search for subtitles")

    def _build_video_file_section(self) -> None:
        section_layout = QVBoxLayout(self)
        section_layout.setContentsMargins(0, 0, 0, 0)

        self._filename_edit = SearchLineEdit("Search for subtitles", parent=self)
        self._filename_edit.setText(
            SEARCH_SUBJECT.search_term + SEARCH_SUBJECT.file_extension if SEARCH_SUBJECT.file_exists else ""
        )
        self._filename_edit.editingFinished.connect(self._on_filename_edited)
        self._filename_edit.returnPressed.connect(self._on_search_clicked)
        self._filename_edit.button_clicked.connect(self._on_search_clicked)

        file_row = QHBoxLayout()
        file_row.setContentsMargins(SEPARATOR_INSET, 0, SEPARATOR_INSET, 10)
        file_row.setSpacing(0)
        side_stretch = round((1 - SEARCH_BAR_WIDTH_FRACTION) * 100 / 2)
        file_row.addStretch(side_stretch)
        file_row.addWidget(self._filename_edit, stretch=round(SEARCH_BAR_WIDTH_FRACTION * 100))
        file_row.addStretch(side_stretch)
        section_layout.addLayout(file_row)

    def _on_search_clicked(self) -> None:
        if self._awaiting_suggestions:
            return
        # Tool buttons do not take focus on click, so editingFinished never fires
        # for a typed search term; commit the field before starting the search.
        self._on_filename_edited()
        typed_term = self._filename_edit.text().strip()
        suggestion_service = self._title_suggestion_service
        if suggestion_service is not None and self._needs_title_suggestions(typed_term):
            self._awaiting_suggestions = True
            self.start_spinner()
            suggestion_service.request(typed_term)
            return
        self.research_requested.emit("", None)

    def start_spinner(self) -> None:
        self._filename_edit.start_spinner()

    def stop_spinner(self) -> None:
        self._filename_edit.stop_spinner()

    def _needs_title_suggestions(self, typed_term: str) -> bool:
        if not typed_term:
            return False
        if typed_term == self._term_without_suggestions:
            return False
        release_info = get_release_info(typed_term)
        return release_info.year == 0 and not release_info.tvseries

    def _on_suggestions_ready(self, typed_term: str, suggestions: list[TitleSuggestion]) -> None:
        if not self._awaiting_suggestions:
            return
        self._awaiting_suggestions = False
        if not suggestions:
            # No popup; the spinner keeps running straight into the search.
            self._search_as_typed(typed_term)
            return
        self.stop_spinner()
        self._suggestion_popup().show_suggestions(suggestions)

    def _on_suggestion_lookup_failed(self, _message: str) -> None:
        if not self._awaiting_suggestions:
            return
        self._awaiting_suggestions = False
        self._search_as_typed(self._filename_edit.text().strip())

    def _suggestion_popup(self) -> TitleSuggestionPopup:
        popup = getattr(self, "_title_suggestion_popup", None)
        if popup is None:
            popup = TitleSuggestionPopup(self._filename_edit)
            popup.suggestion_accepted.connect(self._on_suggestion_accepted)
            popup.dismissed.connect(self._on_suggestions_dismissed)
            self._title_suggestion_popup = popup
        return popup

    def _on_suggestion_accepted(self, suggestion: TitleSuggestion) -> None:
        if suggestion.tvseries and self._season_episode_suggestion_service is not None:
            self._pending_series = suggestion
            self.start_spinner()
            self._season_episode_suggestion_service.request_seasons(suggestion.title, suggestion.imdb_id)
            return
        self._commit_term_and_search(suggestion.search_term(), suggestion.imdb_id, suggestion.tvseries)

    def _on_seasons_ready(self, seasons: list[SeasonSuggestion]) -> None:
        if self._pending_series is None:
            return
        self.stop_spinner()
        numbers = [season.number for season in seasons]
        labels = [season.display_text() for season in seasons]
        popup = self._number_popup()
        self._reconnect_number_chosen(popup, self._on_season_chosen)
        popup.show_numbers(numbers, labels)

    def _on_season_chosen(self, season: int) -> None:
        if self._pending_series is None or self._season_episode_suggestion_service is None:
            return
        self._pending_season = season
        self.start_spinner()
        self._season_episode_suggestion_service.request_episodes(
            self._pending_series.title, self._pending_series.imdb_id, season, self._selected_language_name()
        )

    def _on_episodes_ready(self, season: int, episodes: list[EpisodeSuggestion]) -> None:
        if self._pending_series is None or season != self._pending_season:
            return
        self.stop_spinner()
        numbers = [episode.number for episode in episodes]
        labels = [episode.display_text() for episode in episodes]
        popup = self._number_popup()
        self._reconnect_number_chosen(popup, self._on_episode_chosen)
        popup.show_numbers(numbers, labels)

    def _on_episode_chosen(self, episode: int) -> None:
        if self._pending_series is None:
            return
        series = self._pending_series
        term = f"{series.title} S{self._pending_season:02d}E{episode:02d}"
        self._reset_pending_series()
        self._commit_term_and_search(term, series.imdb_id, True)

    def _on_season_episode_lookup_failed(self, _message: str) -> None:
        if self._pending_series is None:
            return
        # IMDb is unreachable: fall back to a series-level search the user can refine.
        series = self._pending_series
        self._reset_pending_series()
        self._commit_term_and_search(series.search_term(), series.imdb_id, True)

    def _selected_language_name(self) -> str:
        selected = self.store.read(ConfigKey.LANGUAGE_SELECTED)
        return self.store.language_data()[selected]["name"]

    def _reset_pending_series(self) -> None:
        self._pending_series = None
        self._pending_season = 0

    @staticmethod
    def _reconnect_number_chosen(popup: NumberSuggestionPopup, slot) -> None:
        # The popup is reused across the season then episode step. Drop the prior
        # step's slot first, otherwise choosing the episode also fires the season
        # handler and clobbers _pending_season with the episode number.
        try:
            popup.number_chosen.disconnect()
        except RuntimeError:
            pass
        popup.number_chosen.connect(slot)

    def _number_popup(self) -> NumberSuggestionPopup:
        popup = getattr(self, "_season_episode_popup", None)
        if popup is None:
            popup = NumberSuggestionPopup(self._filename_edit)
            popup.dismissed.connect(self._on_season_episode_dismissed)
            self._season_episode_popup = popup
        return popup

    def _on_season_episode_dismissed(self) -> None:
        if self._pending_series is None:
            return
        series = self._pending_series
        self._reset_pending_series()
        self._commit_term_and_search(series.search_term(), series.imdb_id, True)

    def _commit_term_and_search(self, term: str, imdb_id: str, tvseries: bool) -> None:
        self._filename_edit.setText(term)
        self._term_without_suggestions = term
        self._on_filename_edited()
        self.research_requested.emit(imdb_id, tvseries)

    def _on_suggestions_dismissed(self) -> None:
        self._search_as_typed(self._filename_edit.text().strip())

    def _search_as_typed(self, typed_term: str) -> None:
        self._term_without_suggestions = typed_term
        self._on_filename_edited()
        self.research_requested.emit("", None)

    def _on_filename_edited(self) -> None:
        filename = self._filename_edit.text().strip()
        if not filename or filename == self._committed_filename:
            return
        self._committed_filename = filename
        self._video_file_service.rename_active_video(filename)

    def select_dropped_video(self, file_path: Path) -> None:
        self._filename_edit.setText(file_path.name)
        self._term_without_suggestions = file_path.name
        self._committed_filename = file_path.name
        self._video_file_service.select_video(file_path)


class SubtitleCard(SettingsCard):
    search_text_changed = Signal(str)
    search_confirmed = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        description = SETTING_DESCRIPTIONS[CardKey.AVAILABLE_SUBTITLES]
        super().__init__(description.title, parent=parent)
        self.add_header_help(description.explanation)
        self.viewLayout.setContentsMargins(*CARD_BODY_MARGINS)
        self._add_dead_chevron()
        self._search_bar = self._build_search_bar()
        self.add_header_button(self._search_bar)

    def _add_dead_chevron(self) -> None:
        # Purely decorative: the other cards carry a collapse chevron, so this card
        # shows the same expanded-state chevron for header consistency. It is disabled
        # and wired to nothing, so the card cannot collapse.
        chevron = TransparentToolButton(self)
        chevron.setFixedSize(TOOL_BUTTON_SIZE, TOOL_BUTTON_SIZE)
        chevron.setIconSize(QSize(SMALL_ICON_SIZE, SMALL_ICON_SIZE))
        chevron.setIcon(lucide_qicon(LucideIcon.CHEVRON_DOWN, palette.NEUTRAL_3))
        chevron.setEnabled(False)
        self.headerLayout.insertWidget(0, chevron)

    def _build_search_bar(self) -> LineEdit:
        bar = LineEdit(self)
        bar.setPlaceholderText("Filter subtitles…")
        apply_body_font(bar)
        flatten_line_edit(bar)
        bar.setFixedWidth(FILTER_BAR_WIDTH)
        bar.setClearButtonEnabled(True)
        bar.textChanged.connect(self.search_text_changed)
        bar.returnPressed.connect(self.search_confirmed)
        return bar

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._align_filter_bar_to_search_bar()

    def _align_filter_bar_to_search_bar(self) -> None:
        field_area_width = self.width() - 2 * SEPARATOR_INSET
        search_bar_right_inset = SEPARATOR_INSET + round((1 - SEARCH_BAR_WIDTH_FRACTION) / 2 * field_area_width)
        trailing_width = self._header_trailing_width()
        left, top, _, bottom = self.headerLayout.getContentsMargins()
        right_margin = max(ROW_INSET, search_bar_right_inset - trailing_width)
        self.headerLayout.setContentsMargins(left, top, right_margin, bottom)

    def _header_trailing_width(self) -> int:
        spacing = max(self.headerLayout.spacing(), 0)
        filter_index = self._filter_bar_index()
        if filter_index is None:
            return 0
        trailing = 0
        for index in range(filter_index + 1, self.headerLayout.count()):
            widget = self.headerLayout.itemAt(index).widget()
            if widget is not None and widget.isVisible():
                trailing += widget.width() + spacing
        return trailing

    def _filter_bar_index(self) -> int | None:
        for index in range(self.headerLayout.count()):
            if self.headerLayout.itemAt(index).widget() is self._search_bar:
                return index
        return None


class SubtitleActionRow(QWidget):
    def __init__(
        self,
        subtitle: Subtitle,
        store: SettingsStore,
        post_processing_service: PostProcessingServiceProtocol,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._subtitle = subtitle
        self._store = store
        self._post_processing_service = post_processing_service
        self._active_button: RowIconButton | None = None
        self._idle_icons: dict[RowIconButton, LucideIcon] = {}
        self._spinner_progress = 0.0
        self._spinner_timer = QTimer(self)
        self._spinner_timer.setInterval(FRAME_INTERVAL_MS)
        self._spinner_timer.timeout.connect(self._advance_spinner)

        self._delivered_directory: str = ""

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, ROW_INSET, 0)
        layout.setSpacing(ACTION_BUTTON_GAP)
        layout.addStretch(1)

        self._move_button = self._make_action_button(LucideIcon.FILES, self._move_tooltip(), self._unpack_and_move)
        layout.addWidget(self._move_button)

        self._move_rename = self._make_action_button(
            LucideIcon.FILE_PEN,
            self._place_tooltip(),
            self._unpack_rename_and_place,
        )
        if not SEARCH_SUBJECT.file_exists:
            self._move_rename.setEnabled(False)
        layout.addWidget(self._move_rename)

        self._open_location = self._make_action_button(
            LucideIcon.FOLDER_SEARCH,
            "Open the folder this subtitle was delivered to",
            self._open_delivered_directory,
        )
        self._open_location.setIcon(lucide_qicon(LucideIcon.FOLDER_SEARCH, palette.NEUTRAL_3))
        self._open_location.setEnabled(False)
        layout.addWidget(self._open_location)

        self._post_processing_service.succeeded.connect(self._on_succeeded)
        self._post_processing_service.failed.connect(self._on_failed)

    def _move_tooltip(self) -> str:
        return f"Move this subtitle to {self._extraction_directory()}"

    def _place_tooltip(self) -> str:
        if not SEARCH_SUBJECT.file_exists:
            return "Unpack and rename subtitle to video file directory, when file exists"
        return f"Unpack subtitle to match {SEARCH_SUBJECT.name} in {self._video_file_directory()}"

    def _extraction_directory(self) -> str:
        configured = str(self._store.read(ConfigKey.PATHS_EXTRACTION_DIRECTORY)).strip()
        return configured or self._store.resolved_default_directory(ConfigKey.PATHS_EXTRACTION_DIRECTORY)

    def _video_file_directory(self) -> str:
        configured = str(self._store.read(ConfigKey.PATHS_VIDEO_FILE_DIRECTORY)).strip()
        if configured in ("", "."):
            return str(WORKSPACE.file_directory)
        return configured

    def _make_action_button(self, icon: LucideIcon, tooltip: str, slot) -> RowIconButton:
        button = RowIconButton(lucide_qicon(icon, TEXT_COLOR), ROW_HEIGHT, self)
        button.setToolTip(tooltip)
        self._idle_icons[button] = icon
        button.clicked.connect(slot)
        return button

    def _unpack_and_move(self) -> None:
        self._begin_operation(self._move_button)
        self._post_processing_service.unpack_and_move(self._store, self._subtitle)

    def _unpack_rename_and_place(self) -> None:
        self._begin_operation(self._move_rename)
        self._post_processing_service.unpack_rename_and_place(self._store, self._subtitle)

    def _begin_operation(self, button: RowIconButton) -> None:
        self._active_button = button
        self._move_button.setEnabled(False)
        self._move_rename.setEnabled(False)
        self._spinner_progress = 0.0
        self._spinner_timer.start()

    def _advance_spinner(self) -> None:
        self._spinner_progress = (self._spinner_progress + FRAME_INTERVAL_MS / CYCLE_MS) % 1.0
        if self._active_button is not None:
            self._active_button.setIcon(
                QIcon(ripple_pixmap(SMALL_ICON_SIZE, DOWNLOADING_COLOR, self._spinner_progress))
            )

    def _open_delivered_directory(self) -> None:
        if not self._delivered_directory:
            return
        QDesktopServices.openUrl(QUrl.fromLocalFile(self._delivered_directory))

    def _on_succeeded(self, delivered_directory: str) -> None:
        button = self._take_active_button()
        if button is None:
            return
        button.setIcon(lucide_qicon(self._idle_icons[button], SUCCESS_COLOR))
        self._delivered_directory = delivered_directory
        self._open_location.setIcon(lucide_qicon(LucideIcon.FOLDER_SEARCH, TEXT_COLOR))
        self._open_location.setEnabled(True)

    def _on_failed(self, _reason: str) -> None:
        button = self._take_active_button()
        if button is not None:
            button.setIcon(lucide_qicon(self._idle_icons[button], FAILED_COLOR))
        self._open_location.setIcon(lucide_qicon(LucideIcon.FOLDER_SEARCH, FAILED_COLOR))

    def _take_active_button(self) -> RowIconButton | None:
        button = self._active_button
        if button is None:
            return None
        self._spinner_timer.stop()
        self._active_button = None
        self._move_button.setEnabled(True)
        self._move_rename.setEnabled(SEARCH_SUBJECT.file_exists)
        return button


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

        self.items_by_subtitle_id: dict[int, QListWidgetItem] = {}
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
        self.items_by_subtitle_id.clear()
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
        # The ::item:hover stylesheet repaints only the row being entered, so the
        # previously hovered row keeps its highlight when the cursor crosses into
        # the selected row. Repaint the whole viewport on every hover change.
        self.list_widget.entered.connect(lambda _index: self.list_widget.viewport().update())
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

    def _item_for(self, subtitle: Subtitle) -> QListWidgetItem | None:
        return self.items_by_subtitle_id.get(id(subtitle))

    def _attach_action_buttons(self, item: QListWidgetItem, subtitle: Subtitle) -> None:
        if not self._store.read(ConfigKey.SUBTITLE_WORKSPACE_MANUAL_POST_PROCESSING):
            return
        row = SubtitleActionRow(
            subtitle,
            self._store,
            self._post_processing_service,
            self.list_widget,
        )
        self.list_widget.setItemWidget(item, row)

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
