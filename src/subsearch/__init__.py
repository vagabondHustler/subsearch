import sys
import threading
import time
from pathlib import Path

PREF_COUNTER = time.perf_counter()
PACKAGE_PATH = Path(__file__).resolve().parent.as_posix()
HOME_PATH = Path(PACKAGE_PATH).parent.as_posix()
sys.path.append(HOME_PATH)

from subsearch.runtime.logging.logger import log


def _route_uncaught_to_log(exc_type, exc_value, exc_traceback) -> None:
    log.uncaught_exception(exc_type, exc_value, exc_traceback)
    sys.__excepthook__(exc_type, exc_value, exc_traceback)


def _route_uncaught_thread_to_log(args: threading.ExceptHookArgs) -> None:
    thread_name = args.thread.name if args.thread else "unknown"
    log.uncaught_exception(args.exc_type, args.exc_value, args.exc_traceback, origin=f"thread {thread_name}")


sys.excepthook = _route_uncaught_to_log
threading.excepthook = _route_uncaught_thread_to_log

from subsearch.__main__ import Subsearch, main

__all__ = ["Subsearch", "main", "PREF_COUNTER", "PACKAGE_PATH", "HOME_PATH"]
