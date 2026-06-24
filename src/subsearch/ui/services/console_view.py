from PySide6.QtCore import QObject, Signal

from subsearch.runtime.recorder import ConsoleSnapshot
from subsearch.ui.services.console_bridge import CONSOLE_BRIDGE


class ConsoleViewSink(QObject):
    snapshot_received = Signal(object)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._latest: ConsoleSnapshot | None = None
        CONSOLE_BRIDGE.attach(self.receive_snapshot)

    def receive_snapshot(self, snapshot: ConsoleSnapshot) -> None:
        self._latest = snapshot
        self.snapshot_received.emit(snapshot)

    def latest(self) -> ConsoleSnapshot | None:
        return self._latest

    def detach(self) -> None:
        CONSOLE_BRIDGE.detach()
