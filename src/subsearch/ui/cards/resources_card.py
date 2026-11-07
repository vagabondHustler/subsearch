import webbrowser
from typing import Callable
from urllib.parse import urlencode

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QApplication, QGridLayout, QWidget

from subsearch.runtime import crash_report
from subsearch.runtime.config import FILE_PATHS
from subsearch.ui.cards.base import SettingsCard
from subsearch.ui.cards.descriptions import SETTING_DESCRIPTIONS, CardKey
from subsearch.ui.icons.lucide import LucideIcon
from subsearch.ui.services.issue_reporting import ISSUE_TEMPLATE_URL, open_bug_report
from subsearch.ui.theme.metrics import CARD_CONTENT_INSET
from subsearch.ui.widgets.icon_caption_button import (
    CaptionToolButton,
    CaptionToolButtonStyle,
)

REPOSITORY_URL = "https://github.com/vagabondHustler/subsearch"
SECURITY_ADVISORY_URL = "https://github.com/vagabondHustler/subsearch/security/advisories/new"
RESOURCES_GRID_COLUMNS = 3


def _build_prefilled_feature_body() -> str:
    return (
        "#### Summary:\n\n"
        "A clear description of the feature you would like to see.\n\n"
        "#### Problem it solves:\n\n"
        "The problem or limitation that motivates this request.\n\n"
        "#### Proposed solution:\n\n"
        "How you imagine it working.\n\n"
        "#### Alternatives considered:\n\n"
        "Any alternative approaches or workarounds you have thought about.\n\n"
        "#### Additional context:\n\n"
        "Any other details, mockups, or examples that may help.\n"
    )


def _copy_sanitized_log_to_clipboard() -> None:
    QApplication.clipboard().setText(crash_report.read_sanitized_crash_sessions())


def _open_feature_request() -> None:
    query = urlencode(
        {
            "template": "feature_request.md",
            "title": "",
            "labels": "enhancement",
            "body": _build_prefilled_feature_body(),
        }
    )
    webbrowser.open(f"{ISSUE_TEMPLATE_URL}?{query}")


def _open_security_advisory() -> None:
    webbrowser.open(SECURITY_ADVISORY_URL)


def _open_log_directory() -> None:
    QDesktopServices.openUrl(QUrl.fromLocalFile(str(FILE_PATHS.log.parent)))


def _open_repository() -> None:
    webbrowser.open(REPOSITORY_URL)


class ResourcesCard(SettingsCard):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("Resources", parent=parent)
        self.add_header_help(SETTING_DESCRIPTIONS[CardKey.RESOURCES].explanation)

        actions = [
            (LucideIcon.BUG, "Report bug", open_bug_report),
            (LucideIcon.SHIELD, "Report vulnerability", _open_security_advisory),
            (LucideIcon.LIGHTBULB, "Request feature", _open_feature_request),
            (LucideIcon.COPY, "Copy sanitized log to clipboard", _copy_sanitized_log_to_clipboard),
            (LucideIcon.FOLDER_SEARCH, "Open config location", _open_log_directory),
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
        action_button = CaptionToolButton(CaptionToolButtonStyle(icon, caption), parent=self)
        action_button.clicked.connect(on_click)
        return action_button
