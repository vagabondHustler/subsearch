from pathlib import Path

from PySide6.QtCore import QObject, QSize, Qt, QThread, QTimer, Signal
from PySide6.QtWidgets import QApplication, QHBoxLayout, QVBoxLayout, QWidget
from qfluentwidgets import CaptionLabel, ProgressBar, TransparentToolButton

from subsearch.io import app_updater
from subsearch.runtime.config.constants import VERSION
from subsearch.runtime.logging.logger import log
from subsearch.ui.cards.base import SettingsCard
from subsearch.ui.cards.changelog_popup import ChangelogButton
from subsearch.ui.icons.lucide import LucideIcon, lucide_qicon
from subsearch.ui.theme.typography import DISABLED_TEXT_COLOR, TEXT_COLOR, apply_caption_font

UPDATE_IDLE_STATUS = "Check for updates to see if a newer version is available."
UPDATE_BUTTON_ICON_SIZE = 24
UPDATE_BUTTON_SIZE = 32
UPDATE_BUTTON_GROUP_GAP = 16
INSTALLER_HANDOFF_DELAY_MS = 1500


class UpdateWorker(QObject):
    def run(self) -> None:
        raise NotImplementedError


class UpdateCheckWorker(UpdateWorker):
    finished = Signal(object)
    failed = Signal(str)

    def run(self) -> None:
        try:
            self.finished.emit(app_updater.check_for_update())
        except Exception as error:
            log.error(str(error))
            self.failed.emit(str(error))


class UpdateInstallWorker(UpdateWorker):
    progress = Signal(float)
    finished = Signal(str)
    failed = Signal(str)

    def __init__(self, latest_version: str) -> None:
        super().__init__()
        self.latest_version = latest_version

    def run(self) -> None:
        try:
            msi_package_path = app_updater.download_installer(self.latest_version, self.progress.emit)
            self.finished.emit(str(msi_package_path))
        except Exception as error:
            log.error(str(error))
            self.failed.emit(str(error))


class UpdateCard(SettingsCard):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("Update", parent)
        self._thread: QThread | None = None
        self._worker: UpdateWorker | None = None
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

        self.install_button, install_column = self._build_update_button(LucideIcon.ARROW_DOWN_TO_LINE, "Install")
        self.install_button.clicked.connect(self._download_and_install)
        self._apply_install_button_state(False)

        self.check_button, check_column = self._build_update_button(LucideIcon.REFRESH_CW_DOT, "Search")
        self.check_button.clicked.connect(self._check_for_update)

        self.changelog_button, changelog_column = self._build_changelog_button()

        content_row = QHBoxLayout()
        content_row.setContentsMargins(16, 8, 16, 4)
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
        progress_row.setContentsMargins(16, 0, 16, 10)
        progress_row.addWidget(self.progress_bar, stretch=1)
        self.body_layout.addLayout(progress_row)

    def _build_update_button(self, icon: LucideIcon, caption: str) -> tuple[TransparentToolButton, QWidget]:
        button = TransparentToolButton(lucide_qicon(icon, TEXT_COLOR), self)
        button.setFixedSize(UPDATE_BUTTON_SIZE, UPDATE_BUTTON_SIZE)
        button.setIconSize(QSize(UPDATE_BUTTON_ICON_SIZE, UPDATE_BUTTON_ICON_SIZE))

        caption_label = CaptionLabel(caption, self)
        apply_caption_font(caption_label)

        column_widget = QWidget(self)
        column = QVBoxLayout(column_widget)
        column.setContentsMargins(0, 0, 0, 0)
        column.setSpacing(0)
        column.addWidget(button, alignment=Qt.AlignmentFlag.AlignHCenter)
        column.addWidget(caption_label, alignment=Qt.AlignmentFlag.AlignHCenter)
        return button, column_widget

    def _build_changelog_button(self) -> tuple[ChangelogButton, QWidget]:
        button = ChangelogButton(self)
        button.setFixedSize(UPDATE_BUTTON_SIZE, UPDATE_BUTTON_SIZE)
        button.setIconSize(QSize(UPDATE_BUTTON_ICON_SIZE, UPDATE_BUTTON_ICON_SIZE))

        caption_label = CaptionLabel("Changelog", self)
        apply_caption_font(caption_label)

        column_widget = QWidget(self)
        column = QVBoxLayout(column_widget)
        column.setContentsMargins(0, 0, 0, 0)
        column.setSpacing(0)
        column.addWidget(button, alignment=Qt.AlignmentFlag.AlignHCenter)
        column.addWidget(caption_label, alignment=Qt.AlignmentFlag.AlignHCenter)
        return button, column_widget

    def _apply_install_button_state(self, enabled: bool) -> None:
        color = TEXT_COLOR if enabled else DISABLED_TEXT_COLOR
        self.install_button.setIcon(lucide_qicon(LucideIcon.ARROW_DOWN_TO_LINE, color))
        self.install_button.setEnabled(enabled)

    def _run_in_thread(self, worker: UpdateWorker) -> None:
        thread = QThread(self)
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        self._thread = thread
        self._worker = worker
        thread.start()

    def _finish_thread(self) -> None:
        if self._thread is not None:
            self._thread.quit()
            self._thread.wait()
            self._thread = None
            self._worker = None

    def _check_for_update(self) -> None:
        self.check_button.setEnabled(False)
        self._apply_install_button_state(False)
        self.latest_version_label.hide()
        self.status_label.setText("Checking for updates…")
        worker = UpdateCheckWorker()
        worker.finished.connect(self._on_check_finished)
        worker.failed.connect(self._on_check_failed)
        self._run_in_thread(worker)

    def _on_check_finished(self, availability: app_updater.UpdateAvailability) -> None:
        self._finish_thread()
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
        self._finish_thread()
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
        self._run_in_thread(worker)

    def _on_install_progress(self, percentage: float) -> None:
        self.progress_bar.setValue(int(percentage))

    def _on_install_finished(self, msi_package_path: str) -> None:
        self._finish_thread()
        self.progress_bar.hide()
        self.status_label.setText("Launching the installer, closing Subsearch…")
        app_updater.run_installer(Path(msi_package_path))
        QTimer.singleShot(INSTALLER_HANDOFF_DELAY_MS, QApplication.quit)

    def _on_install_failed(self, message: str) -> None:
        self._finish_thread()
        self.progress_bar.hide()
        self.check_button.setEnabled(True)
        self._apply_install_button_state(True)
        self.status_label.setText(f"Download failed: {message}")
