from PySide6.QtCore import QEventLoop
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QSystemTrayIcon

from subsearch.runtime.config import metaclasses
from subsearch.runtime.config.constants import APP_PATHS, VERSION
from subsearch.runtime.logging.logger import log
from subsearch.ui.qt_application import get_application

TOAST_DURATION_MS = 5000
TOAST_REGISTRATION_TIMEOUT_MS = 1000


class SystemTray(metaclass=metaclasses.Singleton):
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
        # The core pipeline runs without QApplication.exec, so toasts only render
        # if events are pumped manually here.
        self.application.processEvents()

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
