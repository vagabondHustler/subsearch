from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QWidget

from subsearch.runtime.config import DEVICE_INFO
from subsearch.runtime.config.defaults import ConfigKey
from subsearch.ui.cards.base import SettingsCard
from subsearch.ui.cards.descriptions import SETTING_DESCRIPTIONS, CardKey
from subsearch.ui.icons.lucide import LucideIcon, lucide_qicon
from subsearch.ui.services.shell_integration import ShellIntegrationService
from subsearch.ui.state.store import SettingsStore
from subsearch.ui.theme.typography import TEXT_COLOR
from subsearch.ui.widgets.icon_caption_button import CaptionedToolButton
from subsearch.ui.widgets.notification_toast import NotificationToast
from subsearch.ui.widgets.setting_rows import (
    FloatInputRow,
    IntInputRow,
    SwitchRow,
)

MINIMUM_NOTIFICATION_DURATION_SECONDS = 0.2
MAXIMUM_NOTIFICATION_DURATION_SECONDS = 60.0
NOTIFICATION_DURATION_DECIMALS = 1
SECONDS_TO_MS = 1000
PREVIEW_BUTTON_SPACING = 48


class NotificationsCard(SettingsCard):
    def __init__(self, store: SettingsStore, parent: QWidget | None = None) -> None:
        super().__init__("Notifications", store, parent=parent)
        self.add_header_help(SETTING_DESCRIPTIONS[CardKey.NOTIFICATIONS].explanation)
        self.system_tray = SwitchRow(ConfigKey.NOTIFICATIONS_SYSTEM_TRAY, store)
        self.display_duration = FloatInputRow(
            ConfigKey.NOTIFICATIONS_DISPLAY_DURATION,
            store,
            MINIMUM_NOTIFICATION_DURATION_SECONDS,
            MAXIMUM_NOTIFICATION_DURATION_SECONDS,
            NOTIFICATION_DURATION_DECIMALS,
        )
        self.play_sound = SwitchRow(ConfigKey.NOTIFICATIONS_PLAY_SOUND, store)
        self.add_row(self.system_tray)
        self.add_row(self.play_sound)
        self.add_row(self.display_duration)

        self.preview_success_button = CaptionedToolButton(
            "Preview success", icon=lucide_qicon(LucideIcon.PICTURE_IN_PICTURE_2, TEXT_COLOR), parent=self
        )
        self.preview_failure_button = CaptionedToolButton(
            "Preview failure", icon=lucide_qicon(LucideIcon.PICTURE_IN_PICTURE_2, TEXT_COLOR), parent=self
        )
        self.body_layout.addLayout(self._build_preview_buttons())

        self.system_tray.toggled.connect(self.display_duration.setEnabled)
        self.system_tray.toggled.connect(self.play_sound.setEnabled)
        self.system_tray.toggled.connect(self._set_preview_buttons_enabled)
        self.display_duration.setEnabled(self.system_tray.switch.isChecked())
        self.play_sound.setEnabled(self.system_tray.switch.isChecked())
        self._set_preview_buttons_enabled(self.system_tray.switch.isChecked())

        self.preview_success_button.clicked.connect(lambda: self._preview_notification(succeeded=True))
        self.preview_failure_button.clicked.connect(lambda: self._preview_notification(succeeded=False))
        self._preview_toast: NotificationToast | None = None

    def _build_preview_buttons(self) -> QHBoxLayout:
        button_row = QHBoxLayout()
        button_row.setContentsMargins(0, 8, 0, 4)
        button_row.setSpacing(PREVIEW_BUTTON_SPACING)
        button_row.addStretch(1)
        button_row.addWidget(self.preview_success_button, alignment=Qt.AlignmentFlag.AlignVCenter)
        button_row.addWidget(self.preview_failure_button, alignment=Qt.AlignmentFlag.AlignVCenter)
        button_row.addStretch(1)
        return button_row

    def _set_preview_buttons_enabled(self, enabled: bool) -> None:
        self.preview_success_button.setEnabled(enabled)
        self.preview_failure_button.setEnabled(enabled)

    def _preview_notification(self, succeeded: bool) -> None:
        if self._preview_toast is not None:
            self._preview_toast.dismiss()
        duration_seconds = self.display_duration.value()
        title = "Subtitle downloaded" if succeeded else "No subtitle found"
        summary = (
            "The matching subtitle was downloaded and saved next to your video."
            if succeeded
            else "No matching subtitle was found for this release."
        )
        toast = NotificationToast(
            title,
            summary,
            succeeded=succeeded,
            hold_duration_ms=round(duration_seconds * SECONDS_TO_MS),
            play_sound=self.play_sound.switch.isChecked(),
        )
        toast.dismissed.connect(self._clear_preview_toast)
        self._preview_toast = toast
        toast.show_above_clock()

    def _clear_preview_toast(self) -> None:
        self._preview_toast = None


class ApplicationCard(SettingsCard):
    def __init__(
        self, store: SettingsStore, shell_service: ShellIntegrationService, parent: QWidget | None = None
    ) -> None:
        super().__init__("Application", store, parent=parent)
        self.store = store
        self.shell_service = shell_service
        self.add_header_help(SETTING_DESCRIPTIONS[CardKey.APPLICATION].explanation)
        self.add_row(SwitchRow(ConfigKey.APPLICATION_MICA_EFFECT, store))
        show_terminal = SwitchRow(ConfigKey.APPLICATION_SHOW_TERMINAL, store)
        show_terminal.toggled.connect(self._on_show_terminal_toggled)
        if DEVICE_INFO.mode != "executable":
            self.add_row(show_terminal)
        self.add_row(SwitchRow(ConfigKey.APPLICATION_SHOW_TRAY_ICON, store))
        self.add_row(SwitchRow(ConfigKey.APPLICATION_SINGLE_INSTANCE, store))

    def _on_show_terminal_toggled(self) -> None:
        self.shell_service.reconcile()


class NetworkCard(SettingsCard):
    def __init__(self, store: SettingsStore, parent: QWidget | None = None) -> None:
        super().__init__("Network", store, parent=parent)
        self.add_header_help(SETTING_DESCRIPTIONS[CardKey.NETWORK].explanation)
        self.add_row(IntInputRow(ConfigKey.NETWORK_REQUEST_CONNECT_TIMEOUT, store, 1, 10))
        self.add_row(IntInputRow(ConfigKey.NETWORK_REQUEST_READ_TIMEOUT, store, 1, 10))


class ProviderDiagnosticsCard(SettingsCard):
    def __init__(self, store: SettingsStore, parent: QWidget | None = None) -> None:
        super().__init__("Provider diagnostics", store, parent=parent)
        self.add_header_help(SETTING_DESCRIPTIONS[CardKey.DIAGNOSTICS_HEADER].explanation)
        self.enabled = SwitchRow(ConfigKey.DIAGNOSTICS_ENABLED, store)
        self.failed_attempts = IntInputRow(ConfigKey.DIAGNOSTICS_FAILED_ATTEMPTS_THRESHOLD, store, 1, 10)
        self.add_row(self.enabled)
        self.add_row(self.failed_attempts)
        self.enabled.toggled.connect(self._apply_enabled_state)
        self._apply_enabled_state(self.enabled.switch.isChecked())

    def _apply_enabled_state(self, enabled: bool) -> None:
        self.failed_attempts.setEnabled(enabled)
