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

from subsearch.runtime.config.constants import APP_PATHS
from subsearch.runtime.models.model import Subtitle
from subsearch.ui import warmup
from subsearch.ui.cards import (
    ApiCard,
    ApplicationCard,
    DownloadManagerCard,
    FileExtensionsCard,
    LanguageCard,
    NetworkCard,
    NotificationsCard,
    PostProcessingCard,
    ProviderDiagnosticsCard,
    ProvidersCard,
    ResourcesCard,
    SearchThresholdCard,
    ShellIntegrationCard,
    SubtitleFiltersCard,
    UpdateCard,
)
from subsearch.ui.cards.download_manager import DownloadManagerInterface
from subsearch.ui.icons.lucide import LucideIcon
from subsearch.ui.navigation import NAVIGATION_ITEM_HEIGHT, enlarge_navigation_icons
from subsearch.ui.qt_application import get_application
from subsearch.ui.state.store import SettingsStore
from subsearch.ui.theme.theme_patch import ACCENT_COLOR, force_fixed_accent_color
from subsearch.ui.theme.typography import TEXT_COLOR, apply_body_font

NAVIGATION_EXPAND_WIDTH = 242
NAVIGATION_TOP_MARGIN = 8


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
    def __init__(self, subtitles: list[Subtitle] | None = None) -> None:
        super().__init__()
        self.setWindowTitle("Subsearch")
        self.setWindowIcon(QIcon(str(APP_PATHS.ui_assets / "subsearch.ico")))
        self.resize(900, 760)
        self.setMicaEffectEnabled(True)
        self._clear_title_bar()

        self.store = SettingsStore(self)
        self._close_validators: list[Callable[[], bool]] = []
        store = self.store

        file_extensions_card = FileExtensionsCard(store)

        language_card = LanguageCard(store)
        providers_card = ProvidersCard(store)
        language_card.selection_changed.connect(providers_card.apply_language_compatibility)

        post_processing_card = PostProcessingCard(store)
        self.register_close_validator(post_processing_card.commit_path_or_revert)

        search_threshold_card = SearchThresholdCard(store)

        search_interface = SettingsInterface(
            "searchInterface",
            [
                language_card,
                SubtitleFiltersCard(store),
                providers_card,
                search_threshold_card,
                post_processing_card,
            ],
        )
        integration_interface = SettingsInterface(
            "integrationInterface",
            [
                ShellIntegrationCard(store, file_extensions_card),
                file_extensions_card,
                NotificationsCard(store),
                DownloadManagerCard(store),
            ],
        )
        application_interface = SettingsInterface(
            "applicationInterface",
            [
                ApplicationCard(store),
                NetworkCard(store),
                ProviderDiagnosticsCard(store),
            ],
        )

        api_interface = SettingsInterface(
            "apiInterface",
            [
                ApiCard(store),
            ],
        )

        about_interface = SettingsInterface(
            "aboutInterface",
            [
                UpdateCard(),
                ResourcesCard(),
            ],
        )

        self.download_manager_interface = DownloadManagerInterface(store, subtitles)
        download_manager_interface = self.download_manager_interface

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

    def _insert_navigation_spacer(self, panel, before_route_key: str) -> None:
        target_widget = panel.items[before_route_key].widget
        layout_index = panel.topLayout.indexOf(target_widget)
        spacer = QWidget(panel)
        spacer.setFixedHeight(NAVIGATION_ITEM_HEIGHT)
        spacer.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        panel.topLayout.insertWidget(layout_index, spacer, 0, Qt.AlignmentFlag.AlignTop)

    def register_close_validator(self, validator: Callable[[], bool]) -> None:
        self._close_validators.append(validator)

    def closeEvent(self, e: QCloseEvent) -> None:
        if all(validator() for validator in self._close_validators):
            self.store.commit()
            super().closeEvent(e)
        else:
            e.ignore()


def _suppress_point_size_warning(message_type: QtMsgType, context, message: str) -> None:
    if "setPointSize" in message:
        return
    sys.stderr.write(f"{message}\n")


def open_settings_window(subtitles: list[Subtitle] | None = None) -> list[Subtitle]:
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
    window = SettingsWindow(subtitles)
    window.show()
    application.exec()
    return window.download_manager_interface.downloaded
