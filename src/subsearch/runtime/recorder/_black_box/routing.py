from subsearch.runtime.recorder.config import LogLevel
from subsearch.runtime.recorder._black_box.formatting import EntryFormatter
from subsearch.runtime.recorder._black_box.standard_out.console_output import ConsoleOutput
from subsearch.runtime.recorder._black_box.standard_error.crash_file_output import CrashFileOutput
from subsearch.runtime.recorder._black_box.standard_out.log_file_output import RotatingLogFileOutput
from subsearch.runtime.recorder._black_box.recorded_entry import RecordedEntry

# DEBUG is the only log-file-only level; everything else is shown on the console.
# BANNER opens a phase, INFO is a transient rolling line, WARNING/ERROR/CRITICAL are reserved lines.
_CONSOLE_LEVELS = frozenset({LogLevel.PHASE, LogLevel.INFO, LogLevel.WARNING, LogLevel.ERROR, LogLevel.CRITICAL})


class EntryRouter:
    def __init__(
        self,
        formatter: EntryFormatter,
        console_output: ConsoleOutput,
        log_file_output: RotatingLogFileOutput,
        crash_file_output: CrashFileOutput,
    ) -> None:
        self._formatter = formatter
        self._console_output = console_output
        self._log_file_output = log_file_output
        self._crash_file_output = crash_file_output

    def route(self, entry: RecordedEntry) -> None:
        if entry.level in _CONSOLE_LEVELS:
            self._console_output.write_entry(entry, self._formatter.console_form(entry))
        if entry.level is not LogLevel.PHASE:
            self._log_file_output.write(self._formatter.log_form(entry))

    def route_crash(self, session: str) -> None:
        self._crash_file_output.write_session(session)

    def tick(self) -> None:
        self._console_output.tick()

    def close(self) -> None:
        self._console_output.close()
