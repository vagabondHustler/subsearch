from PySide6.QtCore import QEventLoop, QObject, QThread

from subsearch.runtime.recorder import LogLevel, capture
from subsearch.ui.core.qt_application import get_application
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
        application = get_application()
        # The toast nests its own QEventLoop and is a QWidget; calling it off the GUI
        # thread deadlocks the loop. Notifications are collected during the search and
        # presented after provider workers join, so this must run on the GUI thread.
        assert QThread.currentThread() is application.thread()
        toast = self._build_toast(title, message)
        loop = QEventLoop()
        toast.dismissed.connect(loop.quit)
        toast.show_above_clock()
        loop.exec()

    def _build_toast(self, title: str, message: str) -> NotificationToast:
        return NotificationToast(
            title,
            message,
            succeeded=title == SUCCESS_TITLE,
            hold_duration_ms=self.display_duration_ms,
            play_sound=self.play_sound,
        )

    def start(self) -> None:
        if not self.enabled:
            return
        capture("Subsearch was added to the system tray", level=LogLevel.DEBUG)

    def stop(self) -> None:
        if not self.enabled:
            return
        capture("Subsearch was removed from the system tray", level=LogLevel.DEBUG)
