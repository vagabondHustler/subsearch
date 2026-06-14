import sys
from pathlib import Path

from PySide6.QtWidgets import QFrame, QTextBrowser, QWidget
from qfluentwidgets import SmoothScrollDelegate

from subsearch.ui.cards.base import SettingsCard
from subsearch.ui.theme.metrics import CARD_CONTENT_INSET
from subsearch.ui.theme.typography import CAPTION_FONT_SIZE, TEXT_COLOR, body_font

LICENSE_FILENAME = "LICENSE"
THIRD_PARTY_FILENAME = "THIRD-PARTY-LICENSES.md"
LICENSE_VIEW_HEIGHT = 320
MISSING_LICENSE_MESSAGE = "Licence file not found in this installation."


def _license_directory() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[4]


def _read_license(filename: str) -> str:
    license_path = _license_directory() / filename
    try:
        return license_path.read_text(encoding="utf-8")
    except OSError:
        return MISSING_LICENSE_MESSAGE


class LicenseView(QTextBrowser):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        caption_font = body_font()
        caption_font.setPixelSize(CAPTION_FONT_SIZE)
        self.setFont(caption_font)
        self.setOpenExternalLinks(True)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setFixedHeight(LICENSE_VIEW_HEIGHT)
        self.setLineWrapMode(QTextBrowser.LineWrapMode.WidgetWidth)
        self.document().setDocumentMargin(0)
        self.setStyleSheet(f"QTextBrowser {{ background: transparent; color: {TEXT_COLOR}; }}")
        self._scroll_delegate = SmoothScrollDelegate(self)


class LicenseCard(SettingsCard):
    def __init__(self, title: str, filename: str, render_as_markdown: bool, parent: QWidget | None = None) -> None:
        super().__init__(title, show_restore_button=False, parent=parent)
        view = LicenseView(self)
        text = _read_license(filename)
        if render_as_markdown:
            view.setMarkdown(text)
        else:
            view.setPlainText(text)
        self.body_layout.setContentsMargins(CARD_CONTENT_INSET, 8, CARD_CONTENT_INSET, 10)
        self.body_layout.addWidget(view)
        self.make_collapsible(collapsed=True)


class SubsearchLicenseCard(LicenseCard):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("Subsearch licence", LICENSE_FILENAME, render_as_markdown=False, parent=parent)


class ThirdPartyLicenseCard(LicenseCard):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("Thirdparty licence", THIRD_PARTY_FILENAME, render_as_markdown=True, parent=parent)
