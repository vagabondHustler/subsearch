import webbrowser
from urllib.parse import urlencode

from PySide6.QtCore import QSize, Qt, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget
from qfluentwidgets import CaptionLabel, TransparentToolButton

from subsearch.runtime.constants import DEVICE_INFO, FILE_PATHS, VERSION
from subsearch.ui.cards.cards import SettingsCard
from subsearch.ui.icons.lucide import LucideIcon, lucide_qicon
from subsearch.ui.theme.typography import TEXT_COLOR, apply_caption_font

BUTTON_ICON_SIZE = 24
BUTTON_SIZE = 32
ICON_SPACING = 48

ISSUE_TEMPLATE_URL = "https://github.com/vagabondHustler/subsearch/issues/new"


def build_prefilled_issue_body() -> str:
    ran_from = "executable" if DEVICE_INFO.mode == "executable" else "source"
    template = (
        "**Describe the bug**\n"
        "A clear and concise description of what the bug is.\n\n"
        "**To Reproduce**\n"
        "Steps to reproduce the behavior:\n\n"
        "**Expected behavior**\n"
        "A clear and concise description of what you expected to happen.\n\n"
        "**Desktop (please complete the following information):**\n"
        f" - OS: {DEVICE_INFO.platform}\n"
        f" - Python version: {DEVICE_INFO.python}\n"
        f" - Ran from: {ran_from}\n"
        " - media filename: \n"
        f" - Version: {VERSION}\n\n"
        "**Additional context**\n"
        "Add any other context about the problem here.\n"
    )
    return template


def open_bug_report() -> None:
    query = urlencode(
        {
            "template": "bug_report.md",
            "title": "[BUG]",
            "labels": "bug",
            "body": build_prefilled_issue_body(),
        }
    )
    webbrowser.open(f"{ISSUE_TEMPLATE_URL}?{query}")


def open_log_directory() -> None:
    QDesktopServices.openUrl(QUrl.fromLocalFile(str(FILE_PATHS.log.parent)))


class BugReportCard(SettingsCard):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("Bug report", parent)

        report_button, report_column = self._build_labelled_button(
            LucideIcon.BUG, "Report bug"
        )
        report_button.clicked.connect(open_bug_report)

        log_button, log_column = self._build_labelled_button(
            LucideIcon.FOLDER_SEARCH, "Open log location"
        )
        log_button.clicked.connect(open_log_directory)

        content_row = QHBoxLayout()
        content_row.setContentsMargins(16, 8, 16, 4)
        content_row.setSpacing(ICON_SPACING)
        content_row.addStretch(1)
        content_row.addWidget(report_column, alignment=Qt.AlignmentFlag.AlignVCenter)
        content_row.addWidget(log_column, alignment=Qt.AlignmentFlag.AlignVCenter)
        content_row.addStretch(1)
        self.body_layout.addLayout(content_row)

    def _build_labelled_button(
        self, icon: LucideIcon, caption: str
    ) -> tuple[TransparentToolButton, QWidget]:
        button = TransparentToolButton(lucide_qicon(icon, TEXT_COLOR), self)
        button.setFixedSize(BUTTON_SIZE, BUTTON_SIZE)
        button.setIconSize(QSize(BUTTON_ICON_SIZE, BUTTON_ICON_SIZE))
        return button, self._wrap_in_column(button, caption)

    def _wrap_in_column(self, button: TransparentToolButton, caption: str) -> QWidget:
        caption_label = CaptionLabel(caption, self)
        apply_caption_font(caption_label)

        column_widget = QWidget(self)
        column = QVBoxLayout(column_widget)
        column.setContentsMargins(0, 0, 0, 0)
        column.setSpacing(0)
        column.addWidget(button, alignment=Qt.AlignmentFlag.AlignHCenter)
        column.addWidget(caption_label, alignment=Qt.AlignmentFlag.AlignHCenter)
        return column_widget
