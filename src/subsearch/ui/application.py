import sys
import webbrowser

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

from subsearch.io import toml_file
from subsearch.runtime.model import Subtitle
from subsearch.runtime.constants import APP_PATHS
from subsearch.ui.cards.cards import (
    ApiCard,
    ApplicationCard,
    DownloadManagerCard,
    FileExtensionsCard,
    LanguageCard,
    NetworkCard,
    NotificationsCard,
    PostProcessingCard,
    ProviderHealthCard,
    ProvidersCard,
    SearchThresholdCard,
    ShellIntegrationCard,
    SubtitleFiltersCard,
)
from subsearch.ui.cards.bug_report_card import BugReportCard
from subsearch.ui.cards.download_manager import DownloadManagerInterface
from subsearch.ui.icons.lucide import LucideIcon
from subsearch.ui.cards.update_card import UpdateCard
from subsearch.ui.navigation import enlarge_navigation_icons
from subsearch.ui.qt_application import get_application
from subsearch.ui.theme.theme_patch import force_fixed_accent_color
from subsearch.ui.theme.typography import apply_body_font

TEXT_COLOR = "#c8c8c7"
ACCENT_COLOR = "#c8c8c7"
GITHUB_URL = "https://github.com/vagabondHustler/subsearch"
NAVIGATION_EXPAND_WIDTH = 242
NAVIGATION_TOP_MARGIN = 8
NAVIGATION_EDGE_MARGIN = 5
CONTENT_GAP_ABOVE_GITHUB = 2


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

        file_extensions_card = FileExtensionsCard()

        language_card = LanguageCard()
        providers_card = ProvidersCard()
        language_card.selection_changed.connect(providers_card.apply_language_compatibility)

        self.post_processing_card = PostProcessingCard()

        search_interface = SettingsInterface(
            "searchInterface",
            [
                language_card,
                SubtitleFiltersCard(),
                providers_card,
                SearchThresholdCard(),
                self.post_processing_card,
            ],
        )
        integration_interface = SettingsInterface(
            "integrationInterface",
            [
                ShellIntegrationCard(file_extensions_card),
                file_extensions_card,
                NotificationsCard(),
                DownloadManagerCard(),
            ],
        )
        application_interface = SettingsInterface(
            "applicationInterface",
            [
                ApplicationCard(),
                NetworkCard(),
                ProviderHealthCard(),
                UpdateCard(),
                BugReportCard(),
            ],
        )

        api_interface = SettingsInterface(
            "apiInterface",
            [
                ApiCard(),
            ],
        )

        self.download_manager_interface = DownloadManagerInterface(subtitles)
        download_manager_interface = self.download_manager_interface

        self.navigationInterface.addItem(
            routeKey="header",
            icon=self.windowIcon(),
            text="Subsearch",
            selectable=False,
        )

        self.addSubInterface(search_interface, LucideIcon.TEXT_SEARCH, "Search", isTransparent=True)
        self.addSubInterface(integration_interface, LucideIcon.MONITOR_COG, "Integration", isTransparent=True)
        self.addSubInterface(
            download_manager_interface, LucideIcon.FOLDER_DOWN, "Download manager", isTransparent=True
        )
        self.addSubInterface(application_interface, LucideIcon.SETTINGS, "Application", isTransparent=True)
        self.addSubInterface(api_interface, LucideIcon.KEY_ROUND, "API", isTransparent=True)

        self.navigationInterface.addItem(
            routeKey="github",
            icon=LucideIcon.HEART_HANDSHAKE,
            text="Go to repository",
            onClick=lambda: webbrowser.open(GITHUB_URL),
            selectable=False,
            position=NavigationItemPosition.BOTTOM,
        )

        self._configure_navigation()
        self._align_content_above_github()

    def _align_content_above_github(self) -> None:
        panel = self.navigationInterface.panel
        github_item = panel.items["github"].widget
        panel_bottom_margin = panel.vBoxLayout.contentsMargins().bottom()
        bottom_margin = panel_bottom_margin + github_item.sizeHint().height() + CONTENT_GAP_ABOVE_GITHUB
        margins = self.widgetLayout.contentsMargins()
        self.widgetLayout.setContentsMargins(
            margins.left(), margins.top(), NAVIGATION_EDGE_MARGIN, bottom_margin
        )

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

    def closeEvent(self, e: QCloseEvent) -> None:
        if self.post_processing_card.commit_path_or_revert():
            toml_file.get_config_session().commit()
            super().closeEvent(e)
        else:
            e.ignore()


def _suppress_point_size_warning(message_type: QtMsgType, context, message: str) -> None:
    if "setPointSize" in message:
        return
    sys.stderr.write(f"{message}\n")


def open_settings_window(subtitles: list[Subtitle] | None = None) -> list[Subtitle]:
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
