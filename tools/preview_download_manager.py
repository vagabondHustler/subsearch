"""
Standalone visual smoke test for the download manager UI.

Run with: python tools/preview_download_manager.py

A manual sanity check you run. Shows every status icon
(pending, animated downloading spinner, success, failed) without touching the
network or filesystem..
"""

import contextlib
import io
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

with contextlib.redirect_stdout(io.StringIO()):
    import qfluentwidgets  # noqa: F401  triggers the Pro ad print, swallowed here

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import QApplication
from qfluentwidgets import FluentWindow, Theme, setTheme, setThemeColor

from subsearch.runtime.models.model import Subtitle
from subsearch.runtime.config.constants import APP_PATHS
from subsearch.ui.cards import download_manager as dm
from subsearch.ui.icons.lucide import LucideIcon
from subsearch.ui.navigation import enlarge_navigation_icons
from subsearch.ui.theme.theme_patch import force_fixed_accent_color

TEXT_COLOR = "#c8c8c7"
ACCENT_COLOR = "#c8c8c7"


SAMPLE_COUNT = 100
PROVIDERS = ("subsource", "opensubtitles", "yifysubtitles")
MOVIE_TITLES = (
    "The.Matrix.1999",
    "Inception.2010",
    "Interstellar.2014",
    "Blade.Runner.2049.2017",
    "Dune.Part.Two.2024",
    "Arrival.2016",
    "The.Dark.Knight.2008",
    "Mad.Max.Fury.Road.2015",
    "Parasite.2019",
    "Whiplash.2014",
)
QUALITIES = (
    "1080p.BluRay.x264-GROUP",
    "720p.WEBRip-ANOTHER",
    "YIFY",
    "HDTV.XviD-OLD",
    "DVDRip-DUSTY",
    "2160p.WEB-DL.x265-HDR",
    "1080p.WEB.H264-CAKES",
)


def make_subtitles() -> list[Subtitle]:
    subtitles = []
    for index in range(SAMPLE_COUNT):
        percentage = max(20, 99 - index)
        provider = PROVIDERS[index % len(PROVIDERS)]
        title = MOVIE_TITLES[index % len(MOVIE_TITLES)]
        quality = QUALITIES[index % len(QUALITIES)]
        subtitles.append(
            Subtitle(
                percentage_result=percentage,
                provider_name=provider,
                subtitle_name=f"{title}.{quality}",
                download_url="https://example.invalid/mock.zip",
                request_data={},
            )
        )
    return subtitles


def stub_network_and_filesystem(interface: dm.DownloadManagerInterface) -> None:
    """Replace the real download with a deterministic mock.

    Even rows succeed, odd rows fail, so you can see every icon/color by clicking.
    """

    def mock_download(item, subtitle: Subtitle) -> None:
        row = interface.list_widget.row(item)
        if row % 2 == 0:
            interface._set_status(item, subtitle, dm.SUCCESS_ICON, dm.SUCCESS_COLOR)
            interface.downloaded.append(subtitle)
        else:
            interface._set_status(item, subtitle, dm.FAILED_ICON, dm.FAILED_COLOR)
            interface.failed.append(subtitle)

    def mock_click(item) -> None:
        row = interface.list_widget.row(item)
        subtitle = interface.items_by_subtitle[row]
        if subtitle in interface.downloaded or subtitle in interface.failed:
            return
        interface._set_status(item, subtitle, dm.DOWNLOADING_ICON, dm.DOWNLOADING_COLOR)
        QTimer.singleShot(1500, lambda: mock_download(item, subtitle))

    interface.list_widget.itemClicked.disconnect()
    interface.list_widget.itemClicked.connect(mock_click)


class MockWindow(FluentWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Download Manager , mock")
        self.setWindowIcon(QIcon(str(APP_PATHS.ui_assets / "subsearch.ico")))
        self.resize(760, 680)
        self.setMicaEffectEnabled(True)

        self.interface = dm.DownloadManagerInterface(make_subtitles())
        stub_network_and_filesystem(self.interface)
        self.addSubInterface(self.interface, LucideIcon.FOLDER_DOWN, "Download manager", isTransparent=True)

        self.navigationInterface.setMenuButtonVisible(False)
        self.navigationInterface.setReturnButtonVisible(False)
        enlarge_navigation_icons(self.navigationInterface.panel)


def main() -> None:
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
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
    window = MockWindow()
    window.show()
    application.exec()


if __name__ == "__main__":
    main()
