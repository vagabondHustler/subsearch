from PySide6.QtCore import QObject, Signal

from subsearch.runtime.logging.logger import log


class ConsoleViewSink(QObject):
    # Mirrors the terminal output into the GUI one-to-one: every line the
    # terminal sink prints arrives via message_received. It fires on the worker
    # thread that drives the run, so consumers must connect with queued
    # connections.
    message_received = Signal(str)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._buffer: list[str] = []
        log.add_sink(self._on_message)

    def _on_message(self, message: str) -> None:
        self._buffer.append(message)
        self.message_received.emit(message)

    def buffer(self) -> list[str]:
        return list(self._buffer)

    def detach(self) -> None:
        log.remove_sink(self._on_message)
