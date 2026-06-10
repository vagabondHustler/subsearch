import webbrowser
from typing import Callable
from urllib.parse import urlencode

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QApplication, QGridLayout, QWidget

from subsearch.runtime.config.constants import (
    DEVICE_INFO,
    FILE_PATHS,
    VERSION,
    VIDEO_FILE,
)
from subsearch.runtime.logging import log_sanitizer
from subsearch.ui.cards.base import SettingsCard
from subsearch.ui.icons.lucide import LucideIcon, lucide_qicon
from subsearch.ui.theme.metrics import CARD_CONTENT_INSET
from subsearch.ui.theme.typography import TEXT_COLOR
from subsearch.ui.widgets.icon_caption_button import CaptionedToolButton

ISSUE_TEMPLATE_URL = "https://github.com/vagabondHustler/subsearch/issues/new"
REPOSITORY_URL = "https://github.com/vagabondHustler/subsearch"
SECURITY_ADVISORY_URL = "https://github.com/vagabondHustler/subsearch/security/advisories/new"
THIRD_PARTY_LICENSES_URL = "https://github.com/vagabondHustler/subsearch/blob/main/THIRD-PARTY-LICENSES.md"
RESOURCES_GRID_COLUMNS = 3
NO_VIDEO_FILE = "none (running in configure mode, no video file was opened)"


def _media_filename() -> str:
    if VIDEO_FILE.file_exists:
        return f"{VIDEO_FILE.filename}{VIDEO_FILE.file_extension}"
    return NO_VIDEO_FILE


def _build_prefilled_issue_body() -> str:
    return (
        "#### Description:\n\n"
        "A clear description of the issue and when it occurs.\n\n"
        "#### Steps to reproduce:\n\n"
        "The steps required to trigger the behaviour.\n\n"
        "#### Environment:\n\n"
        f"- OS: {DEVICE_INFO.platform}\n"
        f"- Python version: {DEVICE_INFO.python}\n"
        f"- Filename: {_media_filename()}\n"
        f"- App version: {VERSION}\n\n"
        "#### Additional context:\n\n"
        "Any other details, logs, or screenshots that may help.\n"
    )


def _open_bug_report() -> None:
    query = urlencode(
        {"template": "bug_report.md", "title": "", "labels": "bug", "body": _build_prefilled_issue_body()}
    )
    webbrowser.open(f"{ISSUE_TEMPLATE_URL}?{query}")


def _copy_sanitized_log_to_clipboard() -> None:
    QApplication.clipboard().setText(log_sanitizer.read_sanitized_crash_sessions())


def _open_security_advisory() -> None:
    webbrowser.open(SECURITY_ADVISORY_URL)


def _open_log_directory() -> None:
    QDesktopServices.openUrl(QUrl.fromLocalFile(str(FILE_PATHS.log.parent)))


def _open_repository() -> None:
    webbrowser.open(REPOSITORY_URL)


def _open_third_party_licenses() -> None:
    webbrowser.open(THIRD_PARTY_LICENSES_URL)


class ResourcesCard(SettingsCard):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("Resources", parent)

        actions = [
            (LucideIcon.BUG, "Report bug", _open_bug_report),
            (LucideIcon.BUG_FILE, "Copy sanitized log", _copy_sanitized_log_to_clipboard),
            (LucideIcon.SHIELD, "Report vulnerability", _open_security_advisory),
            (LucideIcon.FOLDER_SEARCH, "Open log location", _open_log_directory),
            (LucideIcon.SCROLL_TEXT, "View licenses", _open_third_party_licenses),
            (LucideIcon.GITHUB, "View source on GitHub", _open_repository),
        ]
        grid = QGridLayout()
        grid.setContentsMargins(CARD_CONTENT_INSET, 8, CARD_CONTENT_INSET, 10)
        grid.setHorizontalSpacing(24)
        grid.setVerticalSpacing(12)
        for column in range(RESOURCES_GRID_COLUMNS):
            grid.setColumnStretch(column, 1)
        for index, (icon, caption, on_click) in enumerate(actions):
            row = index // RESOURCES_GRID_COLUMNS
            column = index % RESOURCES_GRID_COLUMNS
            grid.addWidget(
                self._build_labelled_action(icon, caption, on_click),
                row,
                column,
                alignment=Qt.AlignmentFlag.AlignHCenter,
            )
        self.body_layout.addLayout(grid)

    def _build_labelled_action(self, icon: LucideIcon, caption: str, on_click: Callable[[], None]) -> QWidget:
        action_button = CaptionedToolButton(caption, icon=lucide_qicon(icon, TEXT_COLOR), parent=self)
        action_button.clicked.connect(on_click)
        return action_button
