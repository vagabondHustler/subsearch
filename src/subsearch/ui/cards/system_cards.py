from PySide6.QtWidgets import QWidget

from subsearch.io import windows_registry
from subsearch.runtime.config.constants import DEVICE_INFO
from subsearch.ui.cards.base import SettingsCard
from subsearch.ui.cards.descriptions import SETTING_DESCRIPTIONS
from subsearch.ui.widgets.setting_rows import SpinBoxRow, SwitchRow, read_value


class NotificationsCard(SettingsCard):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("Notifications", parent)
        self.system_tray = SwitchRow("notifications.system_tray")
        self.summary_notification = SwitchRow("notifications.summary_notification")
        self.add_row(self.system_tray)
        self.add_row(self.summary_notification)
        self.system_tray.toggled.connect(self.summary_notification.set_enabled)
        self.summary_notification.set_enabled(self.system_tray.switch.isChecked())


class DownloadManagerCard(SettingsCard):
    mutually_exclusive_keys = {
        "download.open_manager_on_no_matches",
        "download.always_open_manager",
    }

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("Download manager", parent)
        self.add_row(SwitchRow("download.automatic"))
        self.open_on_no_matches = SwitchRow("download.open_manager_on_no_matches")
        self.always_open = SwitchRow("download.always_open_manager")
        self.add_row(self.open_on_no_matches)
        self.add_row(self.always_open)
        self.open_on_no_matches.toggled.connect(
            lambda checked: self._enforce_mutual_exclusivity(self.always_open, checked)
        )
        self.always_open.toggled.connect(
            lambda checked: self._enforce_mutual_exclusivity(self.open_on_no_matches, checked)
        )

    def _enforce_mutual_exclusivity(self, other_row: SwitchRow, enabled: bool) -> None:
        if enabled and other_row.switch.isChecked():
            other_row.set_checked_silently(False)


class ApplicationCard(SettingsCard):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("Application", parent)
        show_terminal = SwitchRow("application.show_terminal")
        if DEVICE_INFO.mode == "executable":
            show_terminal.set_enabled(False)
        show_terminal.toggled.connect(self._on_show_terminal_toggled)
        self.add_row(show_terminal)
        self.add_row(SwitchRow("application.single_instance"))

    def _on_show_terminal_toggled(self) -> None:
        if read_value("shell_integration.context_menu"):
            windows_registry.write_registry_value_by_key("command")


class NetworkCard(SettingsCard):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("Network", parent)
        self.add_row(SpinBoxRow("network.api_call_limit", 1, 99))
        self.add_row(SpinBoxRow("network.request_connect_timeout", 1, 99))
        self.add_row(SpinBoxRow("network.request_read_timeout", 1, 99))


class ProviderHealthCard(SettingsCard):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("Provider health", parent)
        self.add_header_help(SETTING_DESCRIPTIONS["diagnostics.header"].explanation)
        self.enabled = SwitchRow("diagnostics.enabled")
        self.failed_attempts = SpinBoxRow("diagnostics.failed_attempts_threshold", 1, 99)
        self.add_row(self.enabled)
        self.add_row(self.failed_attempts)
        self.enabled.toggled.connect(self._apply_enabled_state)
        self._apply_enabled_state(self.enabled.switch.isChecked())

    def _apply_enabled_state(self, enabled: bool) -> None:
        self.failed_attempts.setEnabled(enabled)
