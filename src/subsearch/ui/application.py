import sys
from typing import Callable

from PySide6.QtCore import Qt, QtMsgType, qInstallMessageHandler
from PySide6.QtGui import QCloseEvent, QColor, QIcon
from PySide6.QtWidgets import QVBoxLayout, QWidget
from qfluentwidgets import (
    FluentWindow,
    NavigationItemPosition,
    SingleDirectionScrollArea,
    Theme,
    setTheme,
    setThemeColor,
)

from subsearch.io import windows_registry
from subsearch.runtime.config.constants import APP_PATHS
from subsearch.runtime.models.model import SearchOutcome, Subtitle
from subsearch.ui import warmup
from subsearch.ui.cards import (
    ApiCard,
    ApplicationCard,
    FileExtensionsCard,
    LanguageCard,
    NetworkCard,
    NotificationsCard,
    PostProcessingCard,
    ProviderDiagnosticsCard,
    ProvidersCard,
    ResourcesCard,
    SearchThresholdCard,
    SettingsCard,
    ShellIntegrationCard,
    SubtitleFiltersCard,
    UpdateCard,
)
from subsearch.ui.cards.download_manager import DownloadManagerInterface
from subsearch.ui.compat.qfluent import (
    ACCENT_COLOR,
    NAVIGATION_ITEM_HEIGHT,
    enlarge_navigation_icons,
    force_fixed_accent_color,
    forward_navigation_wheel_to_page,
)
from subsearch.ui.icons.lucide import LucideIcon
from subsearch.ui.qt_application import get_application
from subsearch.ui.services.log_panel import LogPanelSink
from subsearch.ui.services.post_processing import (
    PostProcessingService,
    PostProcessingServiceProtocol,
)
from subsearch.ui.services.shell_integration import ShellIntegrationService
from subsearch.ui.services.subtitle_downloads import (
    DownloadServiceProtocol,
    SubtitleDownloadService,
)
from subsearch.ui.services.title_suggestions import TitleSuggestionService
from subsearch.ui.services.video_file import VideoFileService
from subsearch.ui.state.store import SettingsStore
from subsearch.ui.state.tasks import TaskRunner, Worker
from subsearch.ui.theme.typography import TEXT_COLOR, apply_body_font

NAVIGATION_EXPAND_WIDTH = 180
NAVIGATION_TOP_MARGIN = 8


def _collapsible(*cards: SettingsCard) -> list[SettingsCard]:
    for card in cards:
        card.make_collapsible()
    return list(cards)


class SettingsInterface(SingleDirectionScrollArea):
    def __init__(self, object_name: str, cards: list[QWidget]) -> None:
        super().__init__(orient=Qt.Orientation.Vertical)
        self.setObjectName(object_name)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        container = QWidget(self)
        layout = QVBoxLayout(container)
        layout.setContentsMargins(36, 24, 36, 24)
        layout.setSpacing(16)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        for card in cards:
            layout.addWidget(card)

        self.setWidget(container)
        self.enableTransparentBackground()


class SettingsWindow(FluentWindow):
    def __init__(
        self,
        subtitles: list[Subtitle] | None = None,
        search_worker_factory: Callable[[str], Worker] | None = None,
        download_service: DownloadServiceProtocol | None = None,
        post_processing_service: PostProcessingServiceProtocol | None = None,
        start_search_immediately: bool = False,
    ) -> None:
        super().__init__()
        self._search_worker_factory = search_worker_factory
        self._search_running = False
        self.setWindowTitle("Subsearch")
        self.setWindowIcon(QIcon(str(APP_PATHS.ui_assets / "subsearch.ico")))
        self.resize(900, 760)
        self.setMicaEffectEnabled(True)
        self._clear_title_bar()

        self.store = SettingsStore(self)
        self.task_runner = TaskRunner(self)
        self._close_validators: list[Callable[[], bool]] = []
        store = self.store
        shell_service = ShellIntegrationService(self.task_runner, self)
        if download_service is None:
            download_service = SubtitleDownloadService(self.task_runner, self)
        if post_processing_service is None:
            post_processing_service = PostProcessingService(self.task_runner, self)
        in_search_mode = subtitles is not None or search_worker_factory is not None
        log_panel_sink = LogPanelSink(self) if in_search_mode else None

        post_processing_card = PostProcessingCard(store)
        self.register_close_validator(post_processing_card.commit_path_or_revert)

        search_threshold_card = SearchThresholdCard(store)

        search_interface = SettingsInterface(
            "searchInterface",
            [
                *_collapsible(
                    LanguageCard(store),
                    SubtitleFiltersCard(store),
                    ProvidersCard(store),
                    search_threshold_card,
                ),
                # Manages its own collapsibility: collapses while post-processing
                # is handled manually in the download manager.
                post_processing_card,
            ],
        )
        integration_interface = SettingsInterface(
            "integrationInterface",
            _collapsible(
                ShellIntegrationCard(store, shell_service),
                FileExtensionsCard(store, shell_service),
                NotificationsCard(store),
            ),
        )
        application_interface = SettingsInterface(
            "applicationInterface",
            _collapsible(
                ApplicationCard(store, shell_service),
                NetworkCard(store),
                ProviderDiagnosticsCard(store),
            ),
        )

        api_interface = SettingsInterface(
            "apiInterface",
            _collapsible(
                ApiCard(store),
            ),
        )

        about_interface = SettingsInterface(
            "aboutInterface",
            _collapsible(
                UpdateCard(self.task_runner),
                ResourcesCard(),
            ),
        )

        video_file_service = VideoFileService(self)
        title_suggestion_service = TitleSuggestionService(self.task_runner, self)
        self.download_manager_interface = DownloadManagerInterface(
            store,
            download_service,
            post_processing_service,
            video_file_service,
            subtitles,
            log_panel_sink,
            title_suggestion_service,
        )
        download_manager_interface = self.download_manager_interface

        if search_worker_factory is not None:
            self.download_manager_interface.research_requested.connect(self._start_search)
            if start_search_immediately:
                self._start_search("")

        self.navigationInterface.addItem(
            routeKey="header",
            icon=self.windowIcon(),
            text="Subsearch",
            selectable=False,
        )

        self.addSubInterface(search_interface, LucideIcon.TEXT_SEARCH, "Search", isTransparent=True)
        self.addSubInterface(integration_interface, LucideIcon.MONITOR_COG, "Integration", isTransparent=True)
        self.addSubInterface(api_interface, LucideIcon.KEY_ROUND, "API", isTransparent=True)
        self.addSubInterface(application_interface, LucideIcon.SETTINGS, "Application", isTransparent=True)
        self.addSubInterface(download_manager_interface, LucideIcon.FOLDER_DOWN, "Download manager", isTransparent=True)
        self.addSubInterface(
            about_interface,
            LucideIcon.HEART_HANDSHAKE,
            "About",
            isTransparent=True,
            position=NavigationItemPosition.BOTTOM,
        )

        self._configure_navigation()

    def _clear_title_bar(self) -> None:
        getattr(self.titleBar, "iconLabel").hide()
        getattr(self.titleBar, "titleLabel").hide()

    def _configure_navigation(self) -> None:
        panel = self.navigationInterface.panel
        self.navigationInterface.setExpandWidth(NAVIGATION_EXPAND_WIDTH)
        self.navigationInterface.setMenuButtonVisible(False)
        self.navigationInterface.setReturnButtonVisible(False)
        panel.setCollapsible(False)
        panel.vBoxLayout.setContentsMargins(0, NAVIGATION_TOP_MARGIN, 0, 5)
        text_color = QColor(TEXT_COLOR)
        for navigation_item in panel.items.values():
            navigation_item.widget.setTextColor(text_color, text_color)
            apply_body_font(getattr(navigation_item.widget, "itemWidget"))
        panel.items["header"].widget.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self._insert_navigation_spacer(panel, before_route_key="downloadManagerInterface")
        enlarge_navigation_icons(panel)
        forward_navigation_wheel_to_page(panel, self.stackedWidget.currentWidget)

    def _insert_navigation_spacer(self, panel, before_route_key: str) -> None:
        target_widget = panel.items[before_route_key].widget
        layout_index = panel.topLayout.indexOf(target_widget)
        spacer = QWidget(panel)
        spacer.setFixedHeight(NAVIGATION_ITEM_HEIGHT)
        spacer.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        panel.topLayout.insertWidget(layout_index, spacer, 0, Qt.AlignmentFlag.AlignTop)

    def register_close_validator(self, validator: Callable[[], bool]) -> None:
        self._close_validators.append(validator)

    def _start_search(self, imdb_id: str = "") -> None:
        if self._search_worker_factory is None or self._search_running:
            return
        self._search_running = True
        self.download_manager_interface.reset_for_search()
        worker = self._search_worker_factory(imdb_id)
        worker.finished.connect(self._on_search_finished)
        worker.failed.connect(self._on_search_failed)
        self.task_runner.submit(worker)

    def _on_search_finished(self, outcome: SearchOutcome) -> None:
        self._search_running = False
        self.download_manager_interface.populate(outcome.subtitles, outcome.skipped_providers)

    def _on_search_failed(self, message: str) -> None:
        self._search_running = False
        self.download_manager_interface.populate([], [f"Search failed: {message}"])

    def closeEvent(self, e: QCloseEvent) -> None:
        if all(validator() for validator in self._close_validators):
            self.task_runner.shutdown()
            self.store.commit()
            windows_registry.reconcile_shell_integration()
            super().closeEvent(e)
        else:
            e.ignore()


def _suppress_point_size_warning(message_type: QtMsgType, context, message: str) -> None:
    if "setPointSize" in message:
        return
    sys.stderr.write(f"{message}\n")


def open_settings_window(
    subtitles: list[Subtitle] | None = None,
    search_worker_factory: Callable[[str], Worker] | None = None,
    download_service: DownloadServiceProtocol | None = None,
    post_processing_service: PostProcessingServiceProtocol | None = None,
    start_search_immediately: bool = False,
) -> list[Subtitle]:
    warmup.await_warmup()
    qInstallMessageHandler(_suppress_point_size_warning)
    application = get_application()
    setTheme(Theme.DARK)
    setThemeColor(ACCENT_COLOR)
    force_fixed_accent_color()
    application.setStyleSheet(
        f"QLabel, CheckBox, RadioButton, BodyLabel, CaptionLabel, SubtitleLabel, "
        f"TitleLabel, StrongBodyLabel, SpinBox, ComboBox, LineEdit, "
        f"#headerLabel, #titleLabel {{ color: {TEXT_COLOR}; }}"
        f"HeaderCardWidget, CardWidget, SimpleCardWidget, ElevatedCardWidget "
        f"{{ background-color: transparent; border: none; }}"
    )
    window = SettingsWindow(
        subtitles, search_worker_factory, download_service, post_processing_service, start_search_immediately
    )
    window.show()
    application.exec()
    return window.download_manager_interface.downloaded
