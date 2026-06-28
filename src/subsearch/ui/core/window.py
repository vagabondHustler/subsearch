from collections.abc import Sequence
from typing import Callable

from PySide6.QtCore import Qt
from PySide6.QtGui import QCloseEvent, QColor, QIcon
from PySide6.QtWidgets import QSystemTrayIcon, QWidget
from qfluentwidgets import FluentWindow, NavigationItemPosition

from subsearch.runtime.config import APP_PATHS, shell_integration
from subsearch.runtime.config.defaults import ConfigKey
from subsearch.runtime.models import SearchOutcome, Subtitle
from subsearch.runtime.recorder import phase
from subsearch.ui.cards import (
    ApiCard,
    ApplicationCard,
    FileExtensionsCard,
    LanguageCard,
    NetworkCard,
    NotificationsCard,
    PathsCard,
    ProviderDiagnosticsCard,
    ProvidersCard,
    ResourcesCard,
    SearchModeCard,
    SearchThresholdCard,
    ShellIntegrationCard,
    SubsearchLicenseCard,
    SubtitleFiltersCard,
    SubtitleHandlingCard,
    ThirdPartyLicenseCard,
    UpdateCard,
)
from subsearch.ui.cards.subtitle_workspace import ManualSearchInterface
from subsearch.ui.compat.qfluent import (
    enlarge_navigation_icons,
    forward_navigation_wheel_to_page,
)
from subsearch.ui.core._constants import (
    NAVIGATION_EXPAND_WIDTH,
    NAVIGATION_TOP_MARGIN,
    SAVE_CLEAN_COLOR,
    SAVE_DIRTY_COLOR,
)
from subsearch.ui.core.settings_interface import SettingsInterface, _collapsible
from subsearch.ui.icons.lucide import LucideIcon, lucide_qicon
from subsearch.ui.services.console_view import ConsoleViewSink
from subsearch.ui.services.post_processing import (
    PostProcessingService,
    PostProcessingServiceProtocol,
)
from subsearch.ui.services.search import SearchJobProtocol, SearchJobWorker
from subsearch.ui.services.season_episode_suggestions import (
    SeasonEpisodeSuggestionService,
)
from subsearch.ui.services.shell_integration import ShellIntegrationService
from subsearch.ui.services.subtitle_downloads import (
    DownloadServiceProtocol,
    SubtitleDownloadService,
)
from subsearch.ui.services.title_suggestions import TitleSuggestionService
from subsearch.ui.services.video_file import VideoFileService
from subsearch.ui.state.store import SettingsStore
from subsearch.ui.state.tasks import TaskRunner
from subsearch.ui.theme.typography import TEXT_COLOR, apply_body_font
from subsearch.ui.widgets.tray_icon import WindowTrayIcon


class SettingsWindow(FluentWindow):
    def __init__(
        self,
        subtitles: list[Subtitle] | None = None,
        search_job_factory: Callable[..., SearchJobProtocol] | None = None,
        download_service: DownloadServiceProtocol | None = None,
        post_processing_service: PostProcessingServiceProtocol | None = None,
        start_search_immediately: bool = False,
    ) -> None:
        super().__init__()
        self._search_job_factory = search_job_factory
        self._search_running = False
        self.setWindowTitle("Subsearch")
        self.setWindowIcon(QIcon(str(APP_PATHS.ui_assets / "subsearch.ico")))
        self.setMinimumSize(860, 865)
        self.resize(900, 865)
        self._clear_title_bar()

        self.store = SettingsStore(self)
        self.setMicaEffectEnabled(self.store.read(ConfigKey.APPLICATION_MICA_EFFECT))
        self.task_runner = TaskRunner(self)
        self._close_validators: list[Callable[[], bool]] = []
        store = self.store
        shell_service = ShellIntegrationService(self.task_runner, self)
        if download_service is None:
            download_service = SubtitleDownloadService(self.task_runner, self)  # type: ignore
        if post_processing_service is None:
            post_processing_service = PostProcessingService(self.task_runner, self)
        in_search_mode = subtitles is not None or search_job_factory is not None
        console_view_sink = ConsoleViewSink(self) if in_search_mode else None
        self.console_view_sink = console_view_sink

        def build_search_cards() -> Sequence[QWidget]:
            return _collapsible(
                LanguageCard(store),
                SubtitleFiltersCard(store),
                SearchThresholdCard(store),
            )

        def build_subtitle_handling_cards() -> Sequence[QWidget]:
            paths_card = PathsCard(store)
            self.register_close_validator(paths_card.commit_path_or_revert)
            return _collapsible(SubtitleHandlingCard(store), paths_card)

        def build_providers_cards() -> Sequence[QWidget]:
            return _collapsible(
                SearchModeCard(store),
                ProvidersCard(store),
                ProviderDiagnosticsCard(store),
            )

        def build_integration_cards() -> Sequence[QWidget]:
            return _collapsible(
                ShellIntegrationCard(store, shell_service),
                FileExtensionsCard(store, shell_service),
                NotificationsCard(store),
            )

        def build_application_cards() -> Sequence[QWidget]:
            return _collapsible(
                UpdateCard(self.task_runner),
                ApplicationCard(store, shell_service),
                NetworkCard(store),
            )

        def build_api_cards() -> Sequence[QWidget]:
            return _collapsible(ApiCard(store))

        def build_about_cards() -> Sequence[QWidget]:
            return [
                *_collapsible(ResourcesCard()),
                SubsearchLicenseCard(),
                ThirdPartyLicenseCard(),
            ]

        search_interface = SettingsInterface("searchInterface", build_search_cards)
        subtitle_handling_interface = SettingsInterface("subtitleHandlingInterface", build_subtitle_handling_cards)
        providers_interface = SettingsInterface("providersInterface", build_providers_cards)
        integration_interface = SettingsInterface("integrationInterface", build_integration_cards)
        application_interface = SettingsInterface("applicationInterface", build_application_cards)
        api_interface = SettingsInterface("apiInterface", build_api_cards)
        about_interface = SettingsInterface("aboutInterface", build_about_cards)
        self._lazy_interfaces = [
            search_interface,
            subtitle_handling_interface,
            providers_interface,
            integration_interface,
            application_interface,
            api_interface,
            about_interface,
        ]

        video_file_service = VideoFileService(self)
        title_suggestion_service = TitleSuggestionService(self.task_runner, self)
        season_episode_suggestion_service = SeasonEpisodeSuggestionService(self.task_runner, self)
        self.manual_search_interface = ManualSearchInterface(
            store,
            download_service,
            post_processing_service,
            video_file_service,
            subtitles,
            console_view_sink,
            title_suggestion_service,
            season_episode_suggestion_service,
        )
        manual_search_interface = self.manual_search_interface

        if search_job_factory is not None:
            self.manual_search_interface.research_requested.connect(self._start_search)
            if start_search_immediately:
                self._start_search("")

        self.navigationInterface.addItem(
            routeKey="header",
            icon=self.windowIcon(),
            text="Subsearch",
            selectable=False,
        )

        self.addSubInterface(manual_search_interface, LucideIcon.TEXT_SEARCH, "Subtitle workspace", isTransparent=True)
        self.addSubInterface(providers_interface, LucideIcon.LIST_CHECK, "Search preferences", isTransparent=True)
        self.addSubInterface(search_interface, LucideIcon.CAPTIONS, "Subtitle preferences", isTransparent=True)
        self.addSubInterface(
            subtitle_handling_interface, LucideIcon.FILE_ARCHIVE, "Subtitle handling", isTransparent=True
        )
        self.addSubInterface(integration_interface, LucideIcon.MONITOR_COG, "Desktop behaviour", isTransparent=True)
        self.addSubInterface(application_interface, LucideIcon.SETTINGS, "Application", isTransparent=True)
        self.addSubInterface(api_interface, LucideIcon.KEY_ROUND, "API keys", isTransparent=True)
        self.addSubInterface(
            about_interface,
            LucideIcon.HEART_HANDSHAKE,
            "About",
            isTransparent=True,
            position=NavigationItemPosition.BOTTOM,
        )

        self._save_item = self.navigationInterface.addItem(
            routeKey="saveSettings",
            icon=LucideIcon.SAVE,
            text="Save settings",
            onClick=self.store.commit,
            selectable=False,
            position=NavigationItemPosition.BOTTOM,
        )
        self.store.dirty_changed.connect(self._render_save_item_dirty_state)
        self._render_save_item_dirty_state(self.store.has_uncommitted_changes)

        self._configure_navigation()
        self._tray_icon = self._build_tray_icon()
        self._apply_tray_icon_visibility(self.store.read(ConfigKey.APPLICATION_SHOW_TRAY_ICON))
        self.store.value_changed.connect(self._on_setting_changed)

    def _build_tray_icon(self) -> WindowTrayIcon | None:
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return None
        return WindowTrayIcon(self, on_save_config=self.store.commit)

    def _on_setting_changed(self, key: str, value: object) -> None:
        if key == ConfigKey.APPLICATION_SHOW_TRAY_ICON:
            self._apply_tray_icon_visibility(bool(value))
        elif key == ConfigKey.APPLICATION_MICA_EFFECT:
            self.setMicaEffectEnabled(bool(value))

    def _apply_tray_icon_visibility(self, visible: bool) -> None:
        if self._tray_icon is not None:
            self._tray_icon.setVisible(visible)

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
        enlarge_navigation_icons(panel)
        forward_navigation_wheel_to_page(panel, self.stackedWidget.currentWidget)

    def register_close_validator(self, validator: Callable[[], bool]) -> None:
        self._close_validators.append(validator)

    def _start_search(self, imdb_id: str = "", tvseries: bool | None = None) -> None:
        if self._search_job_factory is None or self._search_running:
            return
        self._search_running = True
        self.manual_search_interface.reset_for_search()
        search_job = self._search_job_factory(imdb_id, tvseries)
        worker = SearchJobWorker(search_job)
        worker.finished.connect(self._on_search_finished)
        worker.failed.connect(self._on_search_failed)
        self.task_runner.submit(worker)

    def _on_search_finished(self, outcome: SearchOutcome) -> None:
        self._search_running = False
        self.manual_search_interface.populate(outcome.subtitles, outcome.skipped_providers)
        phase("Idle")

    def _on_search_failed(self, message: str) -> None:
        self._search_running = False
        self.manual_search_interface.populate([], [f"Search failed: {message}"])
        phase("Idle")

    def _render_save_item_dirty_state(self, dirty: bool) -> None:
        color = SAVE_DIRTY_COLOR if dirty else SAVE_CLEAN_COLOR
        self._save_item.setIcon(lucide_qicon(LucideIcon.SAVE, color))
        self._save_item.setEnabled(dirty)

    def closeEvent(self, e: QCloseEvent) -> None:
        if all(validator() for validator in self._close_validators):
            if self._tray_icon is not None:
                self._tray_icon.hide()
            self.task_runner.shutdown()
            self.store.commit()
            shell_integration.reconcile_shell_integration()
            super().closeEvent(e)
        else:
            e.ignore()
