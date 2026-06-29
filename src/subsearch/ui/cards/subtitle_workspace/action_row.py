from typing import Callable

from PySide6.QtCore import QEvent, Qt, QTimer, QUrl
from PySide6.QtGui import QDesktopServices, QEnterEvent, QIcon, QMouseEvent
from PySide6.QtWidgets import QHBoxLayout, QWidget

from subsearch.runtime.config import SEARCH_SUBJECT, WORKSPACE
from subsearch.runtime.config.defaults import ConfigKey
from subsearch.runtime.models import Subtitle
from subsearch.ui.cards.subtitle_workspace._constants import (
    ACTION_BUTTON_GAP,
    DOWNLOADING_COLOR,
    FAILED_COLOR,
    ROW_HEIGHT,
    SUCCESS_COLOR,
)
from subsearch.ui.icons.lucide import LucideIcon, lucide_qicon
from subsearch.ui.services.post_processing import PostProcessingServiceProtocol
from subsearch.ui.state.store import SettingsStore
from subsearch.ui.theme import palette
from subsearch.ui.theme.metrics import ROW_INSET, SMALL_ICON_SIZE
from subsearch.ui.theme.typography import TEXT_COLOR
from subsearch.ui.widgets.ripple_spinner import (
    CYCLE_MS,
    FRAME_INTERVAL_MS,
    ripple_pixmap,
)
from subsearch.ui.widgets.row_icon_button import RowIconButton


class SubtitleActionRow(QWidget):
    def __init__(
        self,
        subtitle: Subtitle,
        store: SettingsStore,
        post_processing_service: PostProcessingServiceProtocol,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._subtitle = subtitle
        self._store = store
        self._post_processing_service = post_processing_service
        self._active_button: RowIconButton | None = None
        self._idle_icons: dict[RowIconButton, LucideIcon] = {}
        self._spinner_progress = 0.0
        self._spinner_timer = QTimer(self)
        self._spinner_timer.setInterval(FRAME_INTERVAL_MS)
        self._spinner_timer.timeout.connect(self._advance_spinner)

        self._delivered_directory: str = ""

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        # This widget covers the whole list row, so the list viewport stops
        # receiving the mouse moves that clear the ::item:hover highlight. Track
        # moves here and repaint the viewport so the hovered row follows the cursor.
        self.setMouseTracking(True)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, ROW_INSET, 0)
        layout.setSpacing(ACTION_BUTTON_GAP)
        layout.addStretch(1)

        self._move_button = self._make_action_button(LucideIcon.FILES, self._move_tooltip(), self._unpack_and_move)
        layout.addWidget(self._move_button)

        self._move_rename = self._make_action_button(
            LucideIcon.FILE_PEN,
            self._place_tooltip(),
            self._unpack_rename_and_place,
        )
        layout.addWidget(self._move_rename)

        self._open_location = self._make_action_button(
            LucideIcon.FOLDER_SEARCH,
            "Open the folder this subtitle was delivered to",
            self._open_delivered_directory,
        )
        self._open_location.setIcon(lucide_qicon(LucideIcon.FOLDER_SEARCH, palette.NEUTRAL_3))
        self._open_location.setEnabled(False)
        layout.addWidget(self._open_location)

        self._post_processing_service.succeeded.connect(self._on_succeeded)
        self._post_processing_service.failed.connect(self._on_failed)

        self._apply_manual_state(bool(store.read(ConfigKey.SUBTITLE_WORKSPACE_MANUAL_POST_PROCESSING)))
        store.subscribe(ConfigKey.SUBTITLE_WORKSPACE_MANUAL_POST_PROCESSING, self._apply_manual_state)

    def enterEvent(self, event: QEnterEvent) -> None:
        self._repaint_list_viewport()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        self._repaint_list_viewport()

    def leaveEvent(self, event: QEvent) -> None:
        self._repaint_list_viewport()

    def _repaint_list_viewport(self) -> None:
        parent = self.parentWidget()
        if parent is not None:
            parent.update()

    def _apply_manual_state(self, manual_enabled: bool) -> None:
        # When automatic post-processing handles delivery, the manual move/rename
        # buttons stay visible but disabled; Open Containing Folder stays usable.
        self._move_button.setEnabled(manual_enabled and self._active_button is None)
        self._move_rename.setEnabled(manual_enabled and SEARCH_SUBJECT.file_exists and self._active_button is None)

    def _move_tooltip(self) -> str:
        return f"Move this subtitle to {self._extraction_directory()}"

    def _place_tooltip(self) -> str:
        if not SEARCH_SUBJECT.file_exists:
            return "Unpack and rename subtitle to video file directory, when file exists"
        return f"Unpack subtitle to match {SEARCH_SUBJECT.name} in {self._video_file_directory()}"

    def _extraction_directory(self) -> str:
        configured = str(self._store.read(ConfigKey.PATHS_EXTRACTION_DIRECTORY)).strip()
        return configured or self._store.resolved_default_directory(ConfigKey.PATHS_EXTRACTION_DIRECTORY)

    def _video_file_directory(self) -> str:
        configured = str(self._store.read(ConfigKey.PATHS_VIDEO_FILE_DIRECTORY)).strip()
        if configured in ("", "."):
            return str(WORKSPACE.file_directory)
        return configured

    def _make_action_button(self, icon: LucideIcon, tooltip: str, slot: Callable[..., None]) -> RowIconButton:
        button = RowIconButton(lucide_qicon(icon, TEXT_COLOR), ROW_HEIGHT, self)
        button.setToolTip(tooltip)
        self._idle_icons[button] = icon
        button.clicked.connect(slot)
        return button

    def trigger_move(self) -> None:
        if self._move_button.isEnabled():
            self._move_button.click()

    def trigger_rename_and_place(self) -> None:
        if self._move_rename.isEnabled():
            self._move_rename.click()

    def trigger_open_location(self) -> None:
        if self._open_location.isEnabled():
            self._open_location.click()

    def has_delivered_directory(self) -> bool:
        return bool(self._delivered_directory)

    def _unpack_and_move(self) -> None:
        self._begin_operation(self._move_button)
        self._post_processing_service.unpack_and_move(self._store, self._subtitle)

    def _unpack_rename_and_place(self) -> None:
        self._begin_operation(self._move_rename)
        self._post_processing_service.unpack_rename_and_place(self._store, self._subtitle)

    def _begin_operation(self, button: RowIconButton) -> None:
        self._active_button = button
        self._move_button.setEnabled(False)
        self._move_rename.setEnabled(False)
        self._spinner_progress = 0.0
        self._spinner_timer.start()

    def _advance_spinner(self) -> None:
        self._spinner_progress = (self._spinner_progress + FRAME_INTERVAL_MS / CYCLE_MS) % 1.0
        if self._active_button is not None:
            self._active_button.setIcon(
                QIcon(ripple_pixmap(SMALL_ICON_SIZE, DOWNLOADING_COLOR, self._spinner_progress))
            )

    def _open_delivered_directory(self) -> None:
        if not self._delivered_directory:
            return
        QDesktopServices.openUrl(QUrl.fromLocalFile(self._delivered_directory))

    def _on_succeeded(self, delivered_directory: str) -> None:
        button = self._take_active_button()
        if button is None:
            return
        button.setIcon(lucide_qicon(self._idle_icons[button], SUCCESS_COLOR))
        self._delivered_directory = delivered_directory
        self._open_location.setIcon(lucide_qicon(LucideIcon.FOLDER_SEARCH, TEXT_COLOR))
        self._open_location.setEnabled(True)

    def _on_failed(self, _reason: str) -> None:
        button = self._take_active_button()
        if button is not None:
            button.setIcon(lucide_qicon(self._idle_icons[button], FAILED_COLOR))
        self._open_location.setIcon(lucide_qicon(LucideIcon.FOLDER_SEARCH, FAILED_COLOR))

    def _take_active_button(self) -> RowIconButton | None:
        button = self._active_button
        if button is None:
            return None
        self._spinner_timer.stop()
        self._active_button = None
        self._apply_manual_state(bool(self._store.read(ConfigKey.SUBTITLE_WORKSPACE_MANUAL_POST_PROCESSING)))
        return button
