import logging
import traceback
from logging.handlers import RotatingFileHandler
from types import TracebackType
from typing import Callable, Optional

from subsearch.runtime.config.constants import APP_PATHS, FILE_PATHS
from subsearch.runtime.config.metaclasses import Singleton
from subsearch.runtime.logging import log_events, log_sanitizer
from subsearch.runtime.models.model import DataclassInstance

LOG_MAX_BYTES = 1_000_000
LOG_SESSIONS_TO_KEEP = 3

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
            older.unlink(missing_ok=True)
            newer.rename(older)


def _build_file_logger() -> logging.Logger:
    APP_PATHS.appdata_subsearch.mkdir(parents=True, exist_ok=True)
    _rotate_session_logs()
    logger = logging.getLogger("subsearch")
    logger.handlers.clear()
    logger.setLevel(logging.DEBUG)
    file_handler = RotatingFileHandler(FILE_PATHS.log, mode="w", maxBytes=LOG_MAX_BYTES, encoding="utf-8")
    file_handler.setFormatter(
        logging.Formatter(
            "%(levelname)s %(module)s:%(lineno)d %(asctime)s.%(msecs)03d: %(message)s", datefmt="%H:%M:%S"
        )
    )
    logger.addHandler(file_handler)
    _write_session_header(file_handler)
    return logger


def _write_session_header(handler: RotatingFileHandler) -> None:
    if handler.stream is not None:
        handler.stream.write(log_events.session_header())
        handler.flush()


class Logger(metaclass=Singleton):
    def __init__(self) -> None:
        self._file_logger = _build_file_logger()
        self._sinks: list[ConsoleSink] = [_terminal_sink]

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
        safe_message = log_sanitizer.sanitize(message)
        self._file_logger.log(LEVELS[level], safe_message, stacklevel=3)
        if to_console:
            for sink in self._sinks:
                sink(safe_message, color, bold)

    def debug(self, message: str, to_console: bool = True) -> None:
        self.write(message, "debug", to_console)

    def info(self, message: str, to_console: bool = True, color: Optional[str] = None) -> None:
        self.write(message, "info", to_console, color)

    def warning(self, message: str, to_console: bool = True, color: Optional[str] = None) -> None:
        self.write(message, "warning", to_console, color)

    def error(self, message: str, to_console: bool = True, color: Optional[str] = None) -> None:
        self.write(message, "error", to_console, color)

    def critical(self, message: str, to_console: bool = True) -> None:
        self.write(message, "critical", to_console)

    def event(self, event_key: str, level: str = "info", to_console: bool = True, **values: object) -> None:
        text, color, bold = log_events.render(event_key, **values)
        self.write(text, level, to_console, color, bold)

    def dataclass(self, instance: DataclassInstance, level: str = "info", to_console: bool = True) -> None:
        for line in log_events.dataclass_lines(instance):
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


log = Logger()
