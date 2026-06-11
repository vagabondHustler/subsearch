from pathlib import Path

from PySide6.QtCore import QSize, Qt, QTimer, Signal
from PySide6.QtGui import QColor, QFont, QIcon
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QListWidgetItem,
    QVBoxLayout,
    QWidget,
)
from qfluentwidgets import BodyLabel, LineEdit, ListWidget, TransparentToolButton

from subsearch.runtime.config.constants import VIDEO_FILE
from subsearch.runtime.models.model import (
    MatchTier,
    Subtitle,
    SubtitleStatus,
    classify_match_tier,
)
from subsearch.ui.cards.base import SettingsCard
from subsearch.ui.cards.descriptions import SETTING_DESCRIPTIONS
from subsearch.ui.icons.lucide import LucideIcon, lucide_qicon, lucide_rotated_qicon
from subsearch.ui.services.log_panel import LogPanelSink
from subsearch.ui.services.post_processing import PostProcessingServiceProtocol
from subsearch.ui.services.subtitle_downloads import DownloadServiceProtocol
from subsearch.ui.services.video_file import VideoFileService
from subsearch.ui.state.store import SettingsStore
from subsearch.ui.theme import palette
from subsearch.ui.theme.metrics import ROW_INSET, SMALL_ICON_SIZE, TOOL_BUTTON_SIZE
from subsearch.ui.theme.typography import (
    BODY_FONT_SIZE,
    SEMI_BOLD,
    TEXT_COLOR,
    apply_body_font,
)
from subsearch.ui.widgets.icon_caption_button import CaptionedToolButton
from subsearch.ui.widgets.log_panel import LogPanel
from subsearch.ui.widgets.setting_rows import (
    FolderPathRow,
    SearchableComboBoxRow,
    SwitchRow,
)

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

DEFAULT_MANAGER_TARGET_PATH = "."
DEFAULT_WORKING_DIRECTORY = ""
WORKING_DIRECTORY_PLACEHOLDER = "Let Subsearch decide (Downloads\\subs)"
IDLE_PLACEHOLDER_TEXT = "Select a video file or type a search term, then press Search"
SEARCHING_PLACEHOLDER_TEXT = "Searching for subtitles…"
NO_RESULTS_PLACEHOLDER_TEXT = "No subtitles found"
DESTINATION_PATH_EXAMPLES = (
    "Where moved subtitles are placed.\n\n"
    "Relative , taken from the video's own folder:\n"
    "    subs\n"
    "    ..\\Subtitles\n\n"
    "Absolute , a fixed path on disk:\n"
    "    C:\\Users\\You\\Subtitles\n"
    "    D:\\Media\\Subs"
)


class DownloadManagerSettingsCard(SettingsCard):
    research_requested = Signal()

    def __init__(
        self, store: SettingsStore, video_file_service: VideoFileService, parent: QWidget | None = None
    ) -> None:
        super().__init__("Download manager settings", store, parent=parent)
        self.store = store
        self._video_file_service = video_file_service
        self.add_header_help(SETTING_DESCRIPTIONS["card.download_manager_settings"].explanation)

        search_mode_values = {"Manual": "manual", "Hybrid": "hybrid", "Automatic": "automatic"}
        self.add_row(SearchableComboBoxRow("download_manager.search_mode", store, search_mode_values))

        self._manually_handle = SwitchRow("download_manager.manually_handle_post_processing", store)
        self.add_row(self._manually_handle)

        self._use_pp_target = SwitchRow("download_manager.use_post_processing_target", store)
        self.add_row(self._use_pp_target)

        self._target_path_row = FolderPathRow("download_manager.target_path", store, DESTINATION_PATH_EXAMPLES)
        self.body_layout.addWidget(self._target_path_row)
        self.register_restore_defaults([("download_manager.target_path", DEFAULT_MANAGER_TARGET_PATH)])

        self._use_pp_target.toggled.connect(self._apply_use_pp_target_state)
        self._apply_use_pp_target_state(self._use_pp_target.switch.isChecked())

        self._working_directory_row = FolderPathRow(
            "download_manager.working_directory",
            store,
            placeholder_text=WORKING_DIRECTORY_PLACEHOLDER,
            dialog_title="Select working folder",
            validate_path=False,
        )
        self.body_layout.addWidget(self._working_directory_row)
        self.register_restore_defaults([("download_manager.working_directory", DEFAULT_WORKING_DIRECTORY)])

        self._build_video_file_section()

    def _apply_use_pp_target_state(self, use_pp: bool) -> None:
        self._target_path_row.setVisible(not use_pp)

    def _build_video_file_section(self) -> None:
        section_layout = QVBoxLayout()
        section_layout.setContentsMargins(0, 0, 0, 0)

        label_row = QHBoxLayout()
        label_row.setContentsMargins(ROW_INSET, 10, ROW_INSET, 4)
        label = BodyLabel("Video file", self)
        apply_body_font(label)
        label_row.addWidget(label, stretch=1)
        section_layout.addLayout(label_row)

        self._filename_edit = LineEdit(self)
        self._filename_edit.setPlaceholderText("No video file selected")
        self._filename_edit.setText(VIDEO_FILE.filename + VIDEO_FILE.file_extension if VIDEO_FILE.file_exists else "")
        apply_body_font(self._filename_edit)
        self._filename_edit.editingFinished.connect(self._on_filename_edited)

        browse_video = CaptionedToolButton("Browse", icon=lucide_qicon(LucideIcon.FOLDER_OPEN, TEXT_COLOR), parent=self)
        browse_video.clicked.connect(self._browse_for_video_file)

        search_video = CaptionedToolButton("Search", icon=lucide_qicon(LucideIcon.SEARCH, TEXT_COLOR), parent=self)
        search_video.clicked.connect(self._on_search_clicked)

        file_row = QHBoxLayout()
        file_row.setContentsMargins(ROW_INSET, 0, ROW_INSET, 10)
        file_row.addWidget(self._filename_edit, stretch=1)
        file_row.addWidget(browse_video)
        file_row.addWidget(search_video)
        section_layout.addLayout(file_row)

        self.body_layout.addLayout(section_layout)

    def _on_search_clicked(self) -> None:
        # Tool buttons do not take focus on click, so editingFinished never fires
        # for a typed search term; commit the field before starting the search.
        self._on_filename_edited()
        self.research_requested.emit()

    def _on_filename_edited(self) -> None:
        filename = self._filename_edit.text().strip()
        if not filename:
            return
        self._video_file_service.rename_active_video(filename)

    def _browse_for_video_file(self) -> None:
        from subsearch.runtime.config.constants import DEFAULT_CONFIG

        extensions = DEFAULT_CONFIG.get("shell_integration", {}).get("file_extensions", {})
        enabled_exts = [ext for ext, enabled in extensions.items() if enabled]
        filter_string = "Video files ({})".format(" ".join(f"*.{ext}" for ext in enabled_exts))
        selected, _ = QFileDialog.getOpenFileName(
            self.window(),
            "Select video file",
            str(VIDEO_FILE.file_directory) if VIDEO_FILE.file_directory != Path("") else "",
            filter_string,
        )
        if not selected:
            return
        selected_path = Path(selected)
        self._filename_edit.setText(selected_path.name)
        self._video_file_service.select_video(selected_path)


class SubtitleCard(SettingsCard):
    search_text_changed = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        description = SETTING_DESCRIPTIONS["download_manager.available_subtitles"]
        super().__init__(description.title, parent=parent)
        self.add_header_help(description.explanation)
        self.viewLayout.setContentsMargins(*CARD_BODY_MARGINS)
        self._search_bar = self._build_search_bar()
        self._search_button = self._build_search_button()
        self._insert_search_into_header()

    def _build_search_button(self) -> TransparentToolButton:
        button = TransparentToolButton(self)
        button.setIcon(lucide_qicon(LucideIcon.SEARCH, palette.NEUTRAL_3))
        button.setFixedSize(TOOL_BUTTON_SIZE, TOOL_BUTTON_SIZE)
        button.setIconSize(QSize(SMALL_ICON_SIZE, SMALL_ICON_SIZE))
        button.setToolTip("Search subtitles")
        button.setCheckable(True)
        button.toggled.connect(self._on_search_toggled)
        return button

    def _build_search_bar(self) -> LineEdit:
        bar = LineEdit(self)
        bar.setPlaceholderText("Filter subtitles…")
        apply_body_font(bar)
        bar.setClearButtonEnabled(True)
        bar.textChanged.connect(self.search_text_changed)
        bar.setVisible(False)
        return bar

    def _insert_search_into_header(self) -> None:
        # Place the search bar directly before the search button in the header row.
        # replaceWidget puts the button where the placeholder was; we insert the bar
        # one position to the left of it.
        self.add_header_button(self._search_button)
        button_index = self.headerLayout.indexOf(self._search_button)
        self.headerLayout.insertWidget(button_index, self._search_bar)

    def _on_search_toggled(self, active: bool) -> None:
        self._search_bar.setVisible(active)
        icon_color = TEXT_COLOR if active else palette.NEUTRAL_3
        self._search_button.setIcon(lucide_qicon(LucideIcon.SEARCH, icon_color))
        if active:
            self._search_bar.setFocus()
        else:
            self._search_bar.clear()


class SubtitleActionRow(QWidget):
    def __init__(
        self,
        subtitle: Subtitle,
        row_text: str,
        text_color: str,
        store: SettingsStore,
        post_processing_service: PostProcessingServiceProtocol,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._subtitle = subtitle
        self._store = store
        self._post_processing_service = post_processing_service

        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 0, 4, 0)
        layout.setSpacing(4)

        icon_label = QLabel(self)
        icon_label.setPixmap(lucide_qicon(SUCCESS_ICON, SUCCESS_COLOR).pixmap(ICON_SIZE, ICON_SIZE))
        layout.addWidget(icon_label)

        label = BodyLabel(row_text, self)
        label.setFont(DownloadManagerInterface._list_font())
        label.setStyleSheet(f"color: {text_color};")
        layout.addWidget(label, stretch=1)

        move_tooltip = f"Unpack and move all subtitles to: {self._target_path_text()}"
        layout.addWidget(self._make_action_button(LucideIcon.FOLDER_OUTPUT, move_tooltip, self._unpack_and_move))

        place_button = self._make_action_button(
            LucideIcon.FILE_OUTPUT,
            "Unpack, rename to match the video file and place it next to the video",
            self._unpack_rename_and_place,
        )
        if not VIDEO_FILE.file_exists:
            place_button.setEnabled(False)
            place_button.setToolTip("Select a video file to rename and place a subtitle next to it")
        layout.addWidget(place_button)

    def _target_path_text(self) -> str:
        if self._store.read("download_manager.use_post_processing_target"):
            return str(self._store.read("post_processing.target_path"))
        return str(self._store.read("download_manager.target_path"))

    def _make_action_button(self, icon: LucideIcon, tooltip: str, slot) -> TransparentToolButton:
        button = TransparentToolButton(self)
        button.setIcon(lucide_qicon(icon, TEXT_COLOR))
        button.setFixedSize(TOOL_BUTTON_SIZE, TOOL_BUTTON_SIZE)
        button.setIconSize(QSize(SMALL_ICON_SIZE, SMALL_ICON_SIZE))
        button.setToolTip(tooltip)
        button.clicked.connect(slot)
        return button

    def _unpack_and_move(self) -> None:
        self._post_processing_service.unpack_and_move(self._store)

    def _unpack_rename_and_place(self) -> None:
        self._post_processing_service.unpack_rename_and_place(self._store)


class DownloadManagerInterface(QWidget):
    research_requested = Signal()

    def __init__(
        self,
        store: SettingsStore,
        download_service: DownloadServiceProtocol,
        post_processing_service: PostProcessingServiceProtocol,
        video_file_service: VideoFileService,
        subtitles: list[Subtitle] | None = None,
        log_panel_sink: LogPanelSink | None = None,
    ) -> None:
        super().__init__()
        self.setObjectName("downloadManagerInterface")
        self._store = store
        self._post_processing_service = post_processing_service
        self.accept_threshold = store.read("search.accept_threshold")
        self.download_service = download_service
        self.subtitles = sorted(subtitles or [], key=self._sort_key, reverse=True)
        self.skipped_providers: list[str] = []
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

        self._settings_card = DownloadManagerSettingsCard(store, video_file_service, self)
        self._settings_card.research_requested.connect(self.research_requested)
        self._settings_card.make_collapsible(collapsed=bool(self.subtitles))
        layout.addWidget(self._settings_card)

        self._card = SubtitleCard(self)
        self._card.search_text_changed.connect(self._filter_list)
        layout.addWidget(self._card, stretch=1)

        if log_panel_sink is not None:
            self._log_panel = LogPanel(log_panel_sink, self)
            layout.addWidget(self._log_panel, stretch=1)

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

    def reset_for_search(self) -> None:
        self._settings_card.set_collapsed(True)
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
        self.accept_threshold = self._store.read("search.accept_threshold")
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
        self.list_widget.setFont(self._list_font())
        self.list_widget.setIconSize(QSize(ICON_SIZE, ICON_SIZE))
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
            if subtitle.status is SubtitleStatus.AUTO_DOWNLOADED:
                self.downloaded.append(subtitle)
                self._render_status(item, subtitle, SUCCESS_ICON, SUCCESS_COLOR)
                self._attach_action_buttons(item, subtitle)
        self.list_widget.itemClicked.connect(self._on_item_clicked)

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

    def _filter_list(self, query: str) -> None:
        if not hasattr(self, "list_widget"):
            return
        lowered = query.lower()
        for row, subtitle in self.subtitles_by_row.items():
            item = self.list_widget.item(row)
            if item is not None:
                item.setHidden(bool(lowered) and lowered not in subtitle.subtitle_name.lower())

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
        if not self._store.read("download_manager.manually_handle_post_processing"):
            return
        row = SubtitleActionRow(
            subtitle,
            self._row_text(subtitle),
            SUCCESS_COLOR,
            self._store,
            self._post_processing_service,
            self.list_widget,
        )
        item.setText("")
        item.setIcon(QIcon())
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
