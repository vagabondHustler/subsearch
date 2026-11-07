import sys
import threading
from pathlib import Path

from subsearch.runtime.startup import PERF_COUNTER

PACKAGE_PATH = Path(__file__).resolve().parent.as_posix()
HOME_PATH = Path(PACKAGE_PATH).parent.as_posix()
sys.path.append(HOME_PATH)

from types import TracebackType
from typing import Callable, Optional

_crash_notifier: Optional[Callable[[], None]] = None


def set_crash_notifier(notifier: Optional[Callable[[], None]]) -> None:
    global _crash_notifier
    _crash_notifier = notifier


def _notify_crash() -> None:
    if _crash_notifier is not None:
        _crash_notifier()


def _route_uncaught(
    exc_type: type[BaseException], exc_value: BaseException, exc_traceback: TracebackType | None
) -> None:
    _notify_crash()
    sys.__excepthook__(exc_type, exc_value, exc_traceback)


def _route_uncaught_thread(args: threading.ExceptHookArgs) -> None:
    _notify_crash()
    threading.__excepthook__(args)


sys.excepthook = _route_uncaught
threading.excepthook = _route_uncaught_thread

from subsearch.__main__ import Subsearch, main

__all__ = ["Subsearch", "main", "set_crash_notifier", "PERF_COUNTER", "PACKAGE_PATH", "HOME_PATH"]
