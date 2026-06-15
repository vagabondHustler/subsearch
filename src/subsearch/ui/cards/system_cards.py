from PySide6.QtWidgets import QWidget

from subsearch.runtime.config import DEVICE_INFO
from subsearch.runtime.keys import CardKey, ConfigKey
from subsearch.ui.cards.base import SettingsCard
from subsearch.ui.cards.descriptions import SETTING_DESCRIPTIONS
from subsearch.ui.services.shell_integration import ShellIntegrationService
from subsearch.ui.state.store import SettingsStore
from subsearch.ui.widgets.setting_rows import IntInputRow, SwitchRow


class NotificationsCard(SettingsCard):
    def __init__(self, store: SettingsStore, parent: QWidget | None = None) -> None:
        super().__init__("Notifications", store, parent=parent)
        self.add_header_help(SETTING_DESCRIPTIONS[CardKey.NOTIFICATIONS].explanation)
        self.system_tray = SwitchRow(ConfigKey.NOTIFICATIONS_SYSTEM_TRAY, store)
        self.summary_notification = SwitchRow(ConfigKey.NOTIFICATIONS_SUMMARY_NOTIFICATION, store)
        self.add_row(self.system_tray)
        self.add_row(self.summary_notification)
        self.system_tray.toggled.connect(self.summary_notification.set_enabled)
        self.summary_notification.set_enabled(self.system_tray.switch.isChecked())


class ApplicationCard(SettingsCard):
    def __init__(
        self, store: SettingsStore, shell_service: ShellIntegrationService, parent: QWidget | None = None
    ) -> None:
        super().__init__("Application", store, parent=parent)
        self.store = store
        self.shell_service = shell_service
        self.add_header_help(SETTING_DESCRIPTIONS[CardKey.APPLICATION].explanation)
        show_terminal = SwitchRow(ConfigKey.APPLICATION_SHOW_TERMINAL, store)
        show_terminal.toggled.connect(self._on_show_terminal_toggled)
        if DEVICE_INFO.mode != "executable":
            self.add_row(show_terminal)
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
