from PySide6.QtWidgets import QWidget

from subsearch.runtime.config.constants import DEVICE_INFO
from subsearch.ui.cards.base import SettingsCard
from subsearch.ui.cards.descriptions import SETTING_DESCRIPTIONS
from subsearch.ui.services.shell_integration import ShellIntegrationService
from subsearch.ui.state.store import SettingsStore
from subsearch.ui.widgets.setting_rows import IntInputRow, SwitchRow


class NotificationsCard(SettingsCard):
    def __init__(self, store: SettingsStore, parent: QWidget | None = None) -> None:
        super().__init__("Notifications", store, parent=parent)
        self.add_header_help(SETTING_DESCRIPTIONS["card.notifications"].explanation)
        self.system_tray = SwitchRow("notifications.system_tray", store)
        self.summary_notification = SwitchRow("notifications.summary_notification", store)
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
        self.add_header_help(SETTING_DESCRIPTIONS["card.application"].explanation)
        show_terminal = SwitchRow("application.show_terminal", store)
        show_terminal.toggled.connect(self._on_show_terminal_toggled)
        if DEVICE_INFO.mode != "executable":
            self.add_row(show_terminal)
        self.add_row(SwitchRow("application.single_instance", store))

    def _on_show_terminal_toggled(self) -> None:
        self.shell_service.reconcile()


class NetworkCard(SettingsCard):
    def __init__(self, store: SettingsStore, parent: QWidget | None = None) -> None:
        super().__init__("Network", store, parent=parent)
        self.add_header_help(SETTING_DESCRIPTIONS["card.network"].explanation)
        self.add_row(IntInputRow("network.api_call_limit", store, 1, 10))
        self.add_row(IntInputRow("network.request_connect_timeout", store, 1, 10))
        self.add_row(IntInputRow("network.request_read_timeout", store, 1, 10))


class ProviderDiagnosticsCard(SettingsCard):
    def __init__(self, store: SettingsStore, parent: QWidget | None = None) -> None:
        super().__init__("Provider diagnostics", store, parent=parent)
        self.add_header_help(SETTING_DESCRIPTIONS["diagnostics.header"].explanation)
        self.enabled = SwitchRow("diagnostics.enabled", store)
        self.failed_attempts = IntInputRow("diagnostics.failed_attempts_threshold", store, 1, 10)
        self.add_row(self.enabled)
        self.add_row(self.failed_attempts)
        self.enabled.toggled.connect(self._apply_enabled_state)
        self._apply_enabled_state(self.enabled.switch.isChecked())

    def _apply_enabled_state(self, enabled: bool) -> None:
        self.failed_attempts.setEnabled(enabled)
