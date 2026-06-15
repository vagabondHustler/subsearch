import io
import logging
import traceback
from logging.handlers import RotatingFileHandler
from types import TracebackType
from typing import Callable, Optional

from subsearch.runtime.config.composition import APP_PATHS, FILE_PATHS
from subsearch.runtime.keys import LogEvent
from subsearch.runtime.logging import events, rendering
from subsearch.runtime.models import DataclassInstance

LOG_MAX_BYTES = 1_000_000
LOG_SESSIONS_TO_KEEP = 3
LOG_FORMAT = "%(asctime)s %(levelname)-8s %(module)s:%(lineno)d  %(message)s"
LOG_DATE_FORMAT = "%H:%M:%S"

LEVELS = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL,
}

ANSI_RESET = "\033[0m"
ANSI_BOLD = "\033[1m"

# Sink signature: (message, hex_color_or_None, bold)
ConsoleSink = Callable[[str, Optional[str], bool], None]


def _ansi_color(hex_color: str) -> str:
    red, green, blue = int(hex_color[1:3], 16), int(hex_color[3:5], 16), int(hex_color[5:7], 16)
    return f"\033[38;2;{red};{green};{blue}m"


def paint(message: str, hex_color: str, bold: bool = False) -> str:
    bold_code = ANSI_BOLD if bold else ""
    return f"{bold_code}{_ansi_color(hex_color)}{message}{ANSI_RESET}"


def _terminal_sink(message: str, color: Optional[str], bold: bool) -> None:
    print(paint(message, color, bold) if color else message)


def _rotate_session_logs() -> None:
    log_path = FILE_PATHS.log
    for index in range(LOG_SESSIONS_TO_KEEP - 1, 0, -1):
        older = log_path.with_suffix(f".{index}.log")
        newer = log_path.with_suffix(f".{index - 1}.log") if index > 1 else log_path
        if newer.exists():
            try:
                older.unlink(missing_ok=True)
                newer.rename(older)
            except PermissionError:
                # another process holds the log open; keep writing without rotating
                return


class SessionBufferHandler(logging.Handler):
    # Holds the current session's records in memory so a crash can copy the
    # session into the durable crash.log without re-reading the open (and
    # rotation-prone) log.log file on disk.
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
    _rotate_session_logs()
    logger = logging.getLogger("subsearch")
    logger.handlers.clear()
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
    file_handler = RotatingFileHandler(FILE_PATHS.log, mode="w", maxBytes=LOG_MAX_BYTES, encoding="utf-8")
    file_handler.setFormatter(formatter)
    _session_buffer.setFormatter(formatter)
    _session_buffer.reset()
    logger.addHandler(file_handler)
    logger.addHandler(_session_buffer)
    _write_session_header(file_handler)
    return logger


def _write_session_header(handler: RotatingFileHandler) -> None:
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
        self._sinks: list[ConsoleSink] = [_terminal_sink]

    @property
    def file_logger(self) -> logging.Logger:
        # Built on first write, not at import, so importing this module never
        # opens (and truncates, via mode="w") the log file on disk.
        if self._file_logger is None:
            self._file_logger = _build_file_logger()
        return self._file_logger

    def add_sink(self, sink: ConsoleSink) -> None:
        self._sinks.append(sink)

    def remove_sink(self, sink: ConsoleSink) -> None:
        self._sinks.remove(sink)

    def write(
        self,
        message: str,
        level: str = "info",
        to_console: bool = True,
        color: Optional[str] = None,
        bold: bool = False,
    ) -> None:
        self.file_logger.log(LEVELS[level], message, stacklevel=3)
        if to_console:
            for sink in self._sinks:
                sink(message, color, bold)

    def debug(self, message: str) -> None:
        self.write(message, "debug", to_console=False)

    def info(self, message: str, to_console: bool = True, color: Optional[str] = None) -> None:
        self.write(message, "info", to_console, color)

    def warning(self, message: str, to_console: bool = True, color: Optional[str] = None) -> None:
        self.write(message, "warning", to_console, color)

    def error(self, message: str, to_console: bool = True, color: Optional[str] = None) -> None:
        self.write(message, "error", to_console, color)

    def critical(self, message: str, to_console: bool = True) -> None:
        self.write(message, "critical", to_console)

    def event(self, event_key: LogEvent, level: str = "info", **values: object) -> None:
        text = rendering.render(event_key, **values)
        self.write(text, level, to_console=event_key in events.CONSOLE_EVENTS)

    def dataclass(self, instance: DataclassInstance, level: str = "info", to_console: bool = True) -> None:
        for line in rendering.dataclass_lines(instance):
            self.write(line, level, to_console)

    def uncaught_exception(
        self,
        exc_type: Optional[type[BaseException]],
        exc_value: Optional[BaseException],
        exc_traceback: Optional[TracebackType],
        origin: str = "main thread",
    ) -> None:
        formatted = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        self.write(f"Uncaught exception on {origin}\n{formatted}", "critical", to_console=False)
        _append_crash_session(_session_buffer.current_session())


log = Logger()
