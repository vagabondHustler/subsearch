import dataclasses
import inspect
import logging as logging
import threading
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Optional

from subsearch.globals import metaclasses
from subsearch.globals.constants import APP_PATHS, FILE_PATHS
from subsearch.globals.dataclasses import GenericDataClass


def capture_call_info(func: Callable[..., Any]) -> Callable[..., Any]:
    def wrapper(*args, **kwargs) -> Any:
        frame = inspect.currentframe().f_back  # type: ignore
        current_time = datetime.now().time()
        call_time = current_time.strftime("%H:%M:%S.%f")[:-3]
        kwargs["call_module"] = frame.f_globals["__name__"].split(".")[-1]  # type: ignore
        kwargs["call_lineno"] = frame.f_lineno  # type: ignore
        kwargs["call_ct"] = call_time
        return func(*args, **kwargs)

    return wrapper


class ANSIEscapeSequences:
    """
    ANSI escape sequences for text colors
    """

    RESET = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


class _Logging(metaclass=metaclasses.Singleton):
    def __init__(self, *args, **kwargs) -> None:
        self.logger_name = kwargs.get("logger_name", "subsearch")
        if not APP_PATHS.appdata_subsearch.exists():
            APP_PATHS.appdata_subsearch.mkdir(parents=True, exist_ok=True)
        self.log_file_path = kwargs.get("debug_log_file", FILE_PATHS.log)
        self._debug_logger = self.create_logger()
        self._lock = threading.Lock()
        self._ansi = ANSIEscapeSequences

    def create_logger(self) -> logging.Logger:
        logger = logging.getLogger(self.logger_name)
        logger.setLevel(logging.DEBUG)
        file_handler = logging.FileHandler(self.log_file_path, mode="w")
        file_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(message)s", datefmt="%H:%M:%S")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        return logger

    def log(self, message: str, **kwargs) -> None:
        with self._lock:
            self._log(message, **kwargs)
            self._print(message, **kwargs)

    def _log(self, message: str, **kwargs) -> None:
        level = kwargs.get("level", "info")
        log_methods = {
            "debug": self._debug_logger.debug,
            "info": self._debug_logger.info,
            "warning": self._debug_logger.warning,
            "error": self._debug_logger.error,
            "critical": self._debug_logger.critical,
        }
        module = kwargs.get("call_module")
        lineno = kwargs.get("call_lineno")
        time = kwargs.get("call_ct")
        log_msg = f"{level.upper()} {module}:{lineno} {time}: {message}"
        log_methods[level](log_msg)

    def _print(self, message, **kwargs) -> None:
        print_allowed = kwargs.get("print_allowed", True)
        hex_color = kwargs.get("hex_color", "#")
        style = kwargs.get("style", "")

        if not print_allowed:
            pass
        elif hex_color == "#" and len(hex_color) == 1:
            print(message)
        elif hex_color.startswith("#") and len(hex_color[1:]) == 6:
            self._color_print(message, hex_color, style)

    def _hex_to_ansi(self, hex_color: str) -> str:
        r, g, b = int(hex_color[1:3], 16), int(hex_color[3:5], 16), int(hex_color[5:7], 16)
        return f"\033[38;2;{r};{g};{b}m"

    def _color_print(self, message: str, hex_color: str, style: str) -> None:
        color_code = self._hex_to_ansi(hex_color)
        style_code = getattr(self._ansi, style.upper()) if style != "" else ""
        print(f"{style_code}{color_code}{message}{self._ansi.RESET}")


class Logger(metaclass=metaclasses.Singleton):
    def __init__(self) -> None:
        self._logger = _Logging()

    def __call__(self, message: str, **kwargs) -> None:
        self.log(message, **kwargs)

    def log(self, message: str, **kwargs) -> None:
        end_new_line = kwargs.get("end_new_line", False)
        self._logger.log(message, **kwargs)
        if end_new_line:
            self._logger.log("", **kwargs)

    @capture_call_info
    def stdout(self, message: str, **kwargs) -> None:
        self(message, **kwargs)

    @capture_call_info
    def brackets(self, message: str, **kwargs) -> None:
        self(f"--- [{message}] ---", hex_color="#fab387", style="bold", **kwargs)

    @capture_call_info
    def subtitle_match(self, provider: str, subtitle_name: str, result: int, threshold: int, **kwargs) -> None:
        if result >= threshold:
            self(f"{provider:<14}{result:>3}% {subtitle_name}", hex_color="#a6e3a1", **kwargs)
        else:
            self(f"{provider:<14}{result:>3}% {subtitle_name}", **kwargs)

    @capture_call_info
    def file_system_action(self, action_type: str, src: Path, dst: Optional[Path] = None, **kwargs) -> None:
        if src.is_file():
            type_ = "file"
        elif src.is_dir():
            type_ = "directory"
        else:
            type_ = "item"

        __src = src.relative_to(src.parent.parent) if src else None
        __dst = dst.relative_to(dst.parent.parent) if dst else None

        action_messages = {
            "remove": rf"Removing {type_}: ...\{__src}",
            "rename": rf"Renaming {type_}: ...\{__src} -> ...\{__dst}",
            "move": rf"Moving {type_}: ...\{__src} -> ...\{__dst}",
            "extract": rf"Extracting archive: ...\{__src} -> ...\{__dst}",
        }

        message = action_messages.get(action_type)

        if not message:
            raise ValueError("Invalid action type")

        self(message, **kwargs)

    @capture_call_info
    def dataclass(self, instance: GenericDataClass, **kwargs) -> None:
        if not dataclasses.is_dataclass(instance):
            raise ValueError("Input is not a dataclass instance.")
        instance_name = f"--- [{instance.__class__.__name__}] ---"
        self(instance_name, hex_color="#fab387", style="bold", **kwargs)
        for field in dataclasses.fields(instance):
            key = field.name
            value = getattr(instance, key)
            padding = " " * (30 - len(key))
            self(f"{key}:{padding}{value}", **kwargs)

    @capture_call_info
    def task_completed(self, **kwargs) -> None:
        self("Tasks completed", level="info", hex_color="#89b4fa", **kwargs)
