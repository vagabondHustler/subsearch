import sys
import webbrowser

from PySide6.QtCore import Qt, QtMsgType, qInstallMessageHandler
from PySide6.QtGui import QCloseEvent, QColor, QFont, QIcon
from PySide6.QtWidgets import QApplication, QVBoxLayout, QWidget
from qfluentwidgets import (
    FluentWindow,
    NavigationItemPosition,
    SingleDirectionScrollArea,
    Theme,
    setTheme,
    setThemeColor,
)

from subsearch.model import Subtitle
from subsearch.runtime.constants import APP_PATHS, VERSION
from subsearch.ui.cards import (
    ApplicationCard,
    DownloadManagerCard,
    FileExtensionsCard,
    LanguageCard,
    NetworkCard,
    NotificationsCard,
    PostProcessingCard,
    ProvidersCard,
    SearchThresholdCard,
    ShellIntegrationCard,
    SubtitleFiltersCard,
)
from subsearch.ui.download_manager import DownloadManagerInterface
from subsearch.ui.lucide import LucideIcon
from subsearch.ui.update_card import UpdateCard
from subsearch.ui.navigation import enlarge_navigation_icons
from subsearch.ui.theme_patch import force_fixed_accent_color
from subsearch.ui.typography import apply_body_font

TEXT_COLOR = "#c8c8c7"
ACCENT_COLOR = "#c8c8c7"
GITHUB_URL = "https://github.com/vagabondHustler/subsearch"
NAVIGATION_EXPAND_WIDTH = 242
TITLE_BAR_HEIGHT = 48
NAVIGATION_ICON_LEFT = 14
NAVIGATION_ICON_TEXT_GAP = 12


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
        self.setWindowTitle(f"Subsearch {VERSION}")
        self.setWindowIcon(QIcon(str(APP_PATHS.gui_assets / "subsearch.ico")))
        self.resize(900, 760)
        self.setMicaEffectEnabled(True)
        self._align_title_bar_with_navigation()

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
                UpdateCard(),
            ],
        )

        self.download_manager_interface = DownloadManagerInterface(subtitles)
        download_manager_interface = self.download_manager_interface

        self.addSubInterface(search_interface, LucideIcon.TEXT_SEARCH, "Search", isTransparent=True)
        self.addSubInterface(integration_interface, LucideIcon.MONITOR_COG, "Integration", isTransparent=True)
        self.addSubInterface(
            download_manager_interface, LucideIcon.FOLDER_DOWN, "Download manager", isTransparent=True
        )
        self.addSubInterface(application_interface, LucideIcon.SETTINGS, "Application", isTransparent=True)

        self.navigationInterface.addItem(
            routeKey="github",
            icon=LucideIcon.HEART_HANDSHAKE,
            text="GitHub",
            onClick=lambda: webbrowser.open(GITHUB_URL),
            selectable=False,
            position=NavigationItemPosition.BOTTOM,
        )

        self._configure_navigation()

    def _align_title_bar_with_navigation(self) -> None:
        self.titleBar.hBoxLayout.setContentsMargins(NAVIGATION_ICON_LEFT, 0, 0, 0)
        self.titleBar.hBoxLayout.setSpacing(NAVIGATION_ICON_TEXT_GAP)

    def _configure_navigation(self) -> None:
        panel = self.navigationInterface.panel
        self.navigationInterface.setExpandWidth(NAVIGATION_EXPAND_WIDTH)
        self.navigationInterface.setMenuButtonVisible(False)
        self.navigationInterface.setReturnButtonVisible(False)
        panel.setCollapsible(False)
        panel.vBoxLayout.setContentsMargins(0, TITLE_BAR_HEIGHT, 0, 5)
        text_color = QColor(TEXT_COLOR)
        for navigation_item in panel.items.values():
            navigation_item.widget.setTextColor(text_color, text_color)
            apply_body_font(navigation_item.widget.itemWidget)
        enlarge_navigation_icons(panel)

    def closeEvent(self, e: QCloseEvent) -> None:
        if self.post_processing_card.commit_path_or_revert():
            super().closeEvent(e)
        else:
            e.ignore()


def _suppress_point_size_warning(message_type: QtMsgType, context, message: str) -> None:
    if "setPointSize" in message:
        return
    sys.stderr.write(f"{message}\n")


def open_settings_window(subtitles: list[Subtitle] | None = None) -> list[Subtitle]:
    qInstallMessageHandler(_suppress_point_size_warning)
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    application = QApplication.instance()
    if not isinstance(application, QApplication):
        application = QApplication(sys.argv)
    application_font = QFont("Segoe UI")
    application_font.setPixelSize(12)
    application_font.setWeight(QFont.Weight.DemiBold)
    application.setFont(application_font)
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
