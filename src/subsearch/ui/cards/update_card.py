from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QApplication, QHBoxLayout, QVBoxLayout, QWidget
from qfluentwidgets import CaptionLabel, ProgressBar

from subsearch.runtime.config.constants import VERSION
from subsearch.ui.cards.base import SettingsCard
from subsearch.ui.cards.changelog_popup import ChangelogButton
from subsearch.ui.cards.descriptions import SETTING_DESCRIPTIONS
from subsearch.ui.icons.lucide import LucideIcon, lucide_qicon
from subsearch.ui.services.app_updates import (
    UpdateAvailability,
    UpdateCheckWorker,
    UpdateInstallWorker,
    launch_installer,
)
from subsearch.ui.state.tasks import TaskRunner
from subsearch.ui.theme.metrics import CARD_CONTENT_INSET, ROW_INSET
from subsearch.ui.theme.typography import (
    DISABLED_TEXT_COLOR,
    TEXT_COLOR,
    apply_caption_font,
)
from subsearch.ui.widgets.icon_caption_button import CaptionedToolButton

UPDATE_IDLE_STATUS = "Check for updates to see if a newer version is available."
UPDATE_BUTTON_ICON_SIZE = 24
UPDATE_BUTTON_SIZE = 32
UPDATE_BUTTON_GROUP_GAP = 16
INSTALLER_HANDOFF_DELAY_MS = 1500


class UpdateCard(SettingsCard):
    def __init__(self, task_runner: TaskRunner, parent: QWidget | None = None) -> None:
        super().__init__("Update", parent=parent)
        self.add_header_help(SETTING_DESCRIPTIONS["card.update"].explanation)
        self._task_runner = task_runner
        self._latest_version = ""

        self.current_version_label = CaptionLabel(f"Installed version  {VERSION}", self)
        apply_caption_font(self.current_version_label)

        self.latest_version_label = CaptionLabel("", self)
        apply_caption_font(self.latest_version_label)
        self.latest_version_label.hide()

        self.status_label = CaptionLabel(UPDATE_IDLE_STATUS, self)
        apply_caption_font(self.status_label)
        self.status_label.setWordWrap(True)

        text_column = QVBoxLayout()
        text_column.setContentsMargins(0, 0, 0, 0)
        text_column.setSpacing(2)
        text_column.addWidget(self.current_version_label)
        text_column.addWidget(self.latest_version_label)
        text_column.addWidget(self.status_label)

        install_column = CaptionedToolButton("Install", parent=self)
        self.install_button = install_column.button
        self.install_button.clicked.connect(self._download_and_install)
        self._apply_install_button_state(False)

        check_column = CaptionedToolButton(
            "Search", icon=lucide_qicon(LucideIcon.REFRESH_CW_DOT, TEXT_COLOR), parent=self
        )
        self.check_button = check_column.button
        self.check_button.clicked.connect(self._check_for_update)

        self.changelog_button = ChangelogButton(self)
        changelog_column = CaptionedToolButton("Changelog", button=self.changelog_button, parent=self)

        content_row = QHBoxLayout()
        content_row.setContentsMargins(CARD_CONTENT_INSET, 8, ROW_INSET, 4)
        content_row.setSpacing(8)
        content_row.addLayout(text_column, stretch=1)
        content_row.addWidget(check_column, alignment=Qt.AlignmentFlag.AlignVCenter)
        content_row.addSpacing(UPDATE_BUTTON_GROUP_GAP)
        content_row.addWidget(changelog_column, alignment=Qt.AlignmentFlag.AlignVCenter)
        content_row.addWidget(install_column, alignment=Qt.AlignmentFlag.AlignVCenter)
        self.body_layout.addLayout(content_row)

        self.progress_bar = ProgressBar(self)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.hide()
        progress_row = QHBoxLayout()
        progress_row.setContentsMargins(ROW_INSET, 0, ROW_INSET, 10)
        progress_row.addWidget(self.progress_bar, stretch=1)
        self.body_layout.addLayout(progress_row)

    def _apply_install_button_state(self, enabled: bool) -> None:
        color = TEXT_COLOR if enabled else DISABLED_TEXT_COLOR
        self.install_button.setIcon(lucide_qicon(LucideIcon.ARROW_DOWN_TO_LINE, color))
        self.install_button.setEnabled(enabled)

    def _check_for_update(self) -> None:
        self.check_button.setEnabled(False)
        self._apply_install_button_state(False)
        self.latest_version_label.hide()
        self.status_label.setText("Checking for updates…")
        worker = UpdateCheckWorker()
        worker.finished.connect(self._on_check_finished)
        worker.failed.connect(self._on_check_failed)
        self._task_runner.submit(worker)

    def _on_check_finished(self, availability: UpdateAvailability) -> None:
        self.check_button.setEnabled(True)
        self._latest_version = availability.latest_version
        self.latest_version_label.setText(f"Latest version  {availability.latest_version}")
        self.latest_version_label.show()
        self.changelog_button.set_changelog(availability.changelog)
        if availability.update_available:
            prerelease = " (pre-release)" if availability.is_prerelease else ""
            self.status_label.setText(f"A new version is available{prerelease}.")
            self._apply_install_button_state(True)
        else:
            self.status_label.setText("You are running the latest version.")

    def _on_check_failed(self, message: str) -> None:
        self.check_button.setEnabled(True)
        self.status_label.setText(f"Could not check for updates: {message}")

    def _download_and_install(self) -> None:
        self._apply_install_button_state(False)
        self.check_button.setEnabled(False)
        self.progress_bar.setValue(0)
        self.progress_bar.show()
        self.status_label.setText(f"Downloading version {self._latest_version}…")
        worker = UpdateInstallWorker(self._latest_version)
        worker.progress.connect(self._on_install_progress)
        worker.finished.connect(self._on_install_finished)
        worker.failed.connect(self._on_install_failed)
        self._task_runner.submit(worker)

    def _on_install_progress(self, percentage: float) -> None:
        self.progress_bar.setValue(int(percentage))

    def _on_install_finished(self, msi_package_path: str) -> None:
        self.progress_bar.hide()
        self.status_label.setText("Launching the installer, closing Subsearch…")
        launch_installer(msi_package_path)
        QTimer.singleShot(INSTALLER_HANDOFF_DELAY_MS, QApplication.quit)

    def _on_install_failed(self, message: str) -> None:
        self.progress_bar.hide()
        self.check_button.setEnabled(True)
        self._apply_install_button_state(True)
        self.status_label.setText(f"Download failed: {message}")
