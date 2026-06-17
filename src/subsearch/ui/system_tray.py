from PySide6.QtCore import QEventLoop, QObject

from subsearch.runtime.logging.events import LogEvent
from subsearch.runtime.logging.logger import log
from subsearch.ui.qt_application import get_application
from subsearch.ui.widgets.notification_gate import notifications_allowed
from subsearch.ui.widgets.notification_toast import NotificationToast

SUCCESS_TITLE = "Search Succeeded"


class SystemTray(QObject):
    def __init__(self, enabled: bool, display_duration_ms: int, play_sound: bool) -> None:
        super().__init__()
        self.enabled = enabled
        self.display_duration_ms = display_duration_ms
        self.play_sound = play_sound

    def display_toast(self, title: str, message: str) -> None:
        if not self.enabled:
            return
        if not notifications_allowed():
            return
        get_application()
        toast = NotificationToast(
            title,
            message,
            succeeded=title == SUCCESS_TITLE,
            hold_duration_ms=self.display_duration_ms,
            play_sound=self.play_sound,
        )
        self._show_and_wait(toast)

    def _show_and_wait(self, toast: NotificationToast) -> None:
        loop = QEventLoop()
        toast.dismissed.connect(loop.quit)
        toast.show_above_clock()
        loop.exec()

    def start(self) -> None:
        if not self.enabled:
            return
        log.event(LogEvent.TRAY_ADDED, level="debug")

    def stop(self) -> None:
        if not self.enabled:
            return
        log.event(LogEvent.TRAY_REMOVED, level="debug")
