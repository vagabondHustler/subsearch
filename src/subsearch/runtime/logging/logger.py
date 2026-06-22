import io
import logging
import sys
import traceback
from dataclasses import dataclass
from types import TracebackType
from typing import TYPE_CHECKING, Callable, Optional

from subsearch.runtime.config.composition import APP_PATHS, FILE_PATHS
from subsearch.runtime.logging import rendering
from subsearch.runtime.logging.events import LogEvent
from subsearch.runtime.models import DataclassInstance

if TYPE_CHECKING:
    from subsearch.runtime.logging.spinner_console import SpinnerConsole

LOG_MAX_BYTES = 1_000_000
CRASH_CLEAR_EVERY_RUNS = 5
LOG_FORMAT = "%(asctime)s %(levelname)-8s %(module)s:%(lineno)d  %(message)s"
LOG_DATE_FORMAT = "%H:%M:%S"

LEVELS = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL,
}

# Sink signature: (message, *, is_banner, title, done_title, is_last). Plain sinks accept and ignore the keywords.
ConsoleSink = Callable[..., None]


@dataclass(frozen=True)
class ConsoleRecord:
    # One console write, captured with the full spinner/banner protocol so a sink
    # attached mid-run (the GUI console) can replay every line through the same
    # state machine the terminal sink used, not just the flat text.
    message: str
    is_banner: bool = False
    title: Optional[str] = None
    done_title: Optional[str] = None
    is_last: bool = False


def _print_sink(
    message: str,
    *,
    is_banner: bool = False,
    title: Optional[str] = None,
    done_title: Optional[str] = None,
    is_last: bool = False,
) -> None:
    print(message)


class SessionBufferHandler(logging.Handler):
    # Holds the current session's records in memory so a crash can copy the
    # session into the durable crash.log without re-reading the open (and
    # truncated-on-startup) log.log file on disk.
    def __init__(self) -> None:
        super().__init__()
        self._buffer = io.StringIO()

    def emit(self, record: logging.LogRecord) -> None:
        self._buffer.write(self.format(record) + "\n")

    def reset(self) -> None:
        self._buffer = io.StringIO()

    def current_session(self) -> str:
        return self._buffer.getvalue()


_session_buffer = SessionBufferHandler()


def _build_file_logger() -> logging.Logger:
    APP_PATHS.appdata_subsearch.mkdir(parents=True, exist_ok=True)
    _clear_crash_log_periodically()
    logger = logging.getLogger("subsearch")
    logger.handlers.clear()
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
    file_handler = logging.FileHandler(FILE_PATHS.log, mode="w", encoding="utf-8")
    file_handler.setFormatter(formatter)
    _session_buffer.setFormatter(formatter)
    _session_buffer.reset()
    logger.addHandler(file_handler)
    logger.addHandler(_session_buffer)
    _write_session_header(file_handler)
    return logger


def _clear_crash_log_periodically() -> None:
    counter_path = FILE_PATHS.crash.with_suffix(".count")
    try:
        run_count = int(counter_path.read_text(encoding="utf-8")) + 1
    except (FileNotFoundError, ValueError):
        run_count = 1
    if run_count >= CRASH_CLEAR_EVERY_RUNS:
        FILE_PATHS.crash.unlink(missing_ok=True)
        run_count = 0
    counter_path.write_text(str(run_count), encoding="utf-8")


def _write_session_header(handler: logging.FileHandler) -> None:
    if handler.stream is not None:
        handler.stream.write(rendering.session_header())
        handler.flush()


def _append_crash_session(session_text: str) -> None:
    if not session_text.strip():
        return
    crash_path = FILE_PATHS.crash
    crash_path.parent.mkdir(parents=True, exist_ok=True)
    with crash_path.open("a", encoding="utf-8") as crash_file:
        crash_file.write(rendering.session_header())
        crash_file.write(session_text)
    if crash_path.stat().st_size > LOG_MAX_BYTES:
        retained = crash_path.read_bytes()[-LOG_MAX_BYTES:]
        crash_path.write_bytes(retained)


class Logger:
    def __init__(self) -> None:
        self._file_logger: Optional[logging.Logger] = None
        self._spinner_console = self._build_terminal_sink()
        terminal_sink: ConsoleSink = self._spinner_console.write if self._spinner_console else _print_sink
        self._sinks: list[ConsoleSink] = [terminal_sink]
        self._console_history: list[ConsoleRecord] = []

    @staticmethod
    def _build_terminal_sink() -> Optional["SpinnerConsole"]:
        if not (hasattr(sys.stdout, "isatty") and sys.stdout.isatty()):
            return None
        from subsearch.runtime.logging.spinner_console import SpinnerConsole

        return SpinnerConsole()

    def close_console(self) -> None:
        if self._spinner_console is not None:
            self._spinner_console.close()

    @property
    def file_logger(self) -> logging.Logger:
        # Built on first write, not at import, so importing this module never
        # opens (and truncates, via mode="w") the log file on disk.
        if self._file_logger is None:
            self._file_logger = _build_file_logger()
        return self._file_logger

    def add_sink(self, sink: ConsoleSink) -> None:
        # Replay this session's console records so a sink attached after the run has
        # already begun (the GUI console) mirrors what has been logged since
        # startup — through the same banner/spinner protocol, not as flat text.
        for record in self._console_history:
            sink(
                record.message,
                is_banner=record.is_banner,
                title=record.title,
                done_title=record.done_title,
                is_last=record.is_last,
            )
        self._sinks.append(sink)

    def remove_sink(self, sink: ConsoleSink) -> None:
        self._sinks.remove(sink)

    def write(
        self,
        message: str,
        level: str = "info",
        *,
        is_banner: bool = False,
        title: Optional[str] = None,
        done_title: Optional[str] = None,
        is_last: bool = False,
    ) -> None:
        self.file_logger.log(LEVELS[level], message, stacklevel=3)
        self._console_history.append(
            ConsoleRecord(
                message=message,
                is_banner=is_banner,
                title=title,
                done_title=done_title,
                is_last=is_last,
            )
        )
        for sink in self._sinks:
            sink(message, is_banner=is_banner, title=title, done_title=done_title, is_last=is_last)

    def end_banner(self) -> None:
        # Closes the active spinner without opening another. Used after the final
        # banner of a run (e.g. cleanup) so its spinner stops instead of ticking
        # forever waiting for a next banner that never comes.
        self._console_history.append(ConsoleRecord(message="", is_last=True))
        for sink in self._sinks:
            sink("", is_last=True)

    def debug(self, message: str) -> None:
        self.write(message, "debug")

    def info(self, message: str) -> None:
        self.write(message, "info")

    def warning(self, message: str) -> None:
        self.write(message, "warning")

    def error(self, message: str) -> None:
        self.write(message, "error")

    def critical(self, message: str) -> None:
        self.write(message, "critical")

    def event(self, event_key: LogEvent, level: str = "info", **values: object) -> None:
        is_banner = event_key == LogEvent.SPINNER
        title = str(values["title"]) if is_banner and "title" in values else None
        done_title = str(values["done_title"]) if is_banner and "done_title" in values else None
        self.write(
            rendering.render(event_key, **values),
            level,
            is_banner=is_banner,
            title=title,
            done_title=done_title,
        )

    def dataclass(self, instance: DataclassInstance, level: str = "info") -> None:
        for line in rendering.dataclass_lines(instance):
            self.write(line, level)

    def uncaught_exception(
        self,
        exc_type: Optional[type[BaseException]],
        exc_value: Optional[BaseException],
        exc_traceback: Optional[TracebackType],
        origin: str = "main thread",
    ) -> None:
        formatted = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        self.write(f"Uncaught exception on {origin}\n{formatted}", "critical")
        _append_crash_session(_session_buffer.current_session())


log = Logger()
