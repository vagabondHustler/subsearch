import io
import logging
import traceback
from types import TracebackType
from typing import Callable, Optional

from subsearch.runtime.config.composition import APP_PATHS, FILE_PATHS
from subsearch.runtime.logging import rendering
from subsearch.runtime.logging.events import LogEvent
from subsearch.runtime.models import DataclassInstance

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

# Sink signature: (message)
ConsoleSink = Callable[[str], None]


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
        self._sinks: list[ConsoleSink] = [print]
        self._console_history: list[str] = []

    @property
    def file_logger(self) -> logging.Logger:
        # Built on first write, not at import, so importing this module never
        # opens (and truncates, via mode="w") the log file on disk.
        if self._file_logger is None:
            self._file_logger = _build_file_logger()
        return self._file_logger

    def add_sink(self, sink: ConsoleSink) -> None:
        # Replay this session's console lines so a sink attached after the run has
        # already begun (the GUI console) mirrors what has been logged since
        # startup, rather than starting empty.
        for message in self._console_history:
            sink(message)
        self._sinks.append(sink)

    def remove_sink(self, sink: ConsoleSink) -> None:
        self._sinks.remove(sink)

    def write(self, message: str, level: str = "info") -> None:
        self.file_logger.log(LEVELS[level], message, stacklevel=3)
        self._console_history.append(message)
        for sink in self._sinks:
            sink(message)

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
        self.write(rendering.render(event_key, **values), level)

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
