import os
import sys
import threading
from pathlib import Path

# Silence the FFmpeg backend banner QtMultimedia logs on first init; must be set
# before any Qt module imports.
os.environ.setdefault("QT_LOGGING_RULES", "qt.multimedia.ffmpeg=false")

from subsearch.runtime.startup import PERF_COUNTER

PACKAGE_PATH = Path(__file__).resolve().parent.as_posix()
HOME_PATH = Path(PACKAGE_PATH).parent.as_posix()
sys.path.append(HOME_PATH)

from types import TracebackType
from typing import Callable, Optional

from subsearch.runtime.logging.logger import log

_crash_notifier: Optional[Callable[[], None]] = None


def set_crash_notifier(notifier: Optional[Callable[[], None]]) -> None:
    global _crash_notifier
    _crash_notifier = notifier


def _notify_crash() -> None:
    if _crash_notifier is not None:
        _crash_notifier()


def _route_uncaught_to_log(
    exc_type: type[BaseException], exc_value: BaseException, exc_traceback: TracebackType | None
) -> None:
    log.uncaught_exception(exc_type, exc_value, exc_traceback)
    _notify_crash()
    sys.__excepthook__(exc_type, exc_value, exc_traceback)


def _route_uncaught_thread_to_log(args: threading.ExceptHookArgs) -> None:
    thread_name = args.thread.name if args.thread else "unknown"
    log.uncaught_exception(args.exc_type, args.exc_value, args.exc_traceback, origin=f"thread {thread_name}")
    _notify_crash()
    threading.__excepthook__(args)


sys.excepthook = _route_uncaught_to_log
threading.excepthook = _route_uncaught_thread_to_log

from subsearch.__main__ import Subsearch, main

__all__ = ["Subsearch", "main", "set_crash_notifier", "PERF_COUNTER", "PACKAGE_PATH", "HOME_PATH"]
