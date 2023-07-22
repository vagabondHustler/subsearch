import dataclasses
import logging
import threading
from pathlib import Path
from typing import Optional, Type

from subsearch.data.constants import APP_PATHS
from subsearch.utils import decorators


@decorators.singleton
class Logger:
    """
    Singleton logging class
    """

    def __init__(self, *args, **kwargs) -> None:
        self.initialized = True
        debug_log_file = APP_PATHS.app_data_local / "subsearch.log"
        self.debug_logger = self.create_logger(debug_log_file, "debug")

    def create_logger(self, log_file: Path, level: str) -> logging.Logger:
        logger = logging.getLogger(level)
        logger.setLevel(logging.DEBUG)
        file_handler = logging.FileHandler(log_file, mode="w")
        file_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", datefmt="%d-%b-%y %H:%M:%S")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        return logger

    def close_log_file(self) -> None:
        for handler in self.debug_logger.handlers:
            if isinstance(handler, logging.FileHandler):
                handler.close()

    @decorators.thread_safe_log
    def log(self, message: str, level: str, print_allowed: bool = True) -> None:
        log_methods = {
            "debug": self.debug_logger.debug,
            "info": self.debug_logger.info,
            "warning": self.debug_logger.warning,
            "error": self.debug_logger.error,
            "critical": self.debug_logger.critical,
        }

        log_methods[level](message)
        if print_allowed:
            print(message)


_logger = Logger()


def stdout(message: str, level: str = "info", **kwargs) -> None:
    print_allowed = kwargs.get("print_allowed", True)
    end_new_line = kwargs.get("end_new_line", False)

    _logger.log(message, level, print_allowed)
    if end_new_line:
        _logger.log("", level, print_allowed)


def stdout_in_brackets(message: str, **kwargs) -> None:
    stdout(f"--- [{message}] ---", **kwargs)


def stdout_match(provider: str, subtitle_name: str, result: int, threshold: int, **kwargs) -> None:
    if result >= threshold:
        stdout(f"> {provider:<14}{result:>3}% {subtitle_name}", kwargs.get("level", "info"))
    else:
        stdout(f"  {provider:<14}{result:>3}% {subtitle_name}", kwargs.get("level", "info"))


def stdout_path_action(action_type: str, src: Path, dst: Optional[Path] = None, **kwargs) -> None:
    """
    Logs a message indicating the removal, renaming, moving, or extraction of a file or directory.

    Args:
        action_type (str): A string representing the type of action being performed (e.g. "remove", "rename", "move", "extract").
        src (Path): A Path object representing the file or directory being acted upon.
        dst (Path, optional): An optional Path object representing the new location or name of the file or directory (used for renaming, moving and extracting actions). Defaults to None.

    Returns:
        None
    """
    if src.is_file():
        type_ = "file"
    elif src.is_dir():
        type_ = "directory"
    else:
        return None

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

    stdout(message, **kwargs)


def stdout_dataclass(instance: Type[dataclasses.dataclass], **kwargs) -> None:
    if not dataclasses.is_dataclass(instance):
        raise ValueError("Input is not a dataclass instance.")
    stdout_in_brackets(instance.__class__.__name__, **kwargs)
    for field in dataclasses.fields(instance):
        key = field.name
        value = getattr(instance, key)
        padding = " " * (30 - len(key))
        stdout(f"{key}:{padding}{value}", **kwargs)
