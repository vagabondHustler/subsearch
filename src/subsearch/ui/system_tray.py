from PySide6.QtCore import QEventLoop
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QSystemTrayIcon

from subsearch.runtime.config import APP_PATHS, VERSION
from subsearch.runtime.logging.logger import log
from subsearch.ui.qt_application import get_application

TOAST_DURATION_MS = 5000
TOAST_REGISTRATION_TIMEOUT_MS = 1000


class SystemTray:
    def __init__(self, enabled: bool) -> None:
        self.enabled = enabled
        if not self.enabled:
            return
        self.application = get_application()
        icon = QIcon(str(APP_PATHS.ui_assets / "subsearch.ico"))
        self.tray = QSystemTrayIcon(icon)
        self.tray.setToolTip(f"Subsearch {VERSION}")

    def display_toast(self, title: str, msg: str) -> None:
        if not self.enabled:
            return
        self.tray.showMessage(title, msg, QSystemTrayIcon.MessageIcon.Information, TOAST_DURATION_MS)
        # The core pipeline runs without QApplication.exec, so the balloon only
        # reaches the shell if events are pumped over its registration window;
        # a single processEvents fires showMessage before Windows can render it.
        self.application.processEvents(QEventLoop.ProcessEventsFlag.AllEvents, TOAST_REGISTRATION_TIMEOUT_MS)

    def start(self) -> None:
        if not self.enabled:
            return
        self.tray.show()
        self.application.processEvents()
        log.debug("Subsearch was added to the system tray")

    def stop(self) -> None:
        if not self.enabled:
            return
        self.application.processEvents(QEventLoop.ProcessEventsFlag.AllEvents, TOAST_REGISTRATION_TIMEOUT_MS)
        self.tray.hide()
        log.debug("Subsearch was removed from the system tray")
