from typing import Callable

from rich.console import Console

from subsearch.runtime.recorder._black_box.recorded_entry import RecordedEntry
from subsearch.runtime.recorder._black_box.standard_out.spinner_display import (
    SpinnerDisplay,
)
from subsearch.runtime.recorder.config import ConsoleSnapshot, LogLevel


class ConsoleOutput:
    def __init__(
        self,
        callbacks: tuple[Callable[[ConsoleSnapshot], None], ...],
        transient_window_size: int,
        log_name: str,
    ) -> None:
        self._callbacks = callbacks
        self._spinner_display = SpinnerDisplay(Console(), transient_window_size, log_name)

    def write_entry(self, entry: RecordedEntry, console_form: str) -> None:
        if entry.level is LogLevel.PHASE:
            self._spinner_display.open_group(console_form)
        else:
            self._spinner_display.add_line(console_form, str(entry.level))
        self._emit_snapshot()

    def tick(self) -> None:
        self._spinner_display.tick()
        self._emit_snapshot()

    def close(self) -> None:
        self._spinner_display.close()
        self._emit_snapshot()

    def _emit_snapshot(self) -> None:
        snapshot = self._spinner_display.snapshot()
        for callback in self._callbacks:
            callback(snapshot)
