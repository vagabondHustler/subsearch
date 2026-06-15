from typing import Optional

from PySide6.QtCore import QObject, Signal

from subsearch.runtime.logging.logger import log


class LogPanelSink(QObject):
    # Emitted on the thread that called Logger.write — always use queued connections
    # when connecting to GUI-thread slots.
    message_received = Signal(str, str, bool)  # (message, hex_color, bold)

    _FALLBACK_COLOR = "#d3d3d3"  # palette.NEUTRAL_1

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._buffer: list[tuple[str, str, bool]] = []
        log.add_sink(self._on_message)

    def _on_message(self, message: str, color: Optional[str], bold: bool) -> None:
        resolved_color = color if color else self._FALLBACK_COLOR
        entry = (message, resolved_color, bold)
        self._buffer.append(entry)
        self.message_received.emit(*entry)

    def buffer(self) -> list[tuple[str, str, bool]]:
        return list(self._buffer)

    def detach(self) -> None:
        log.remove_sink(self._on_message)
