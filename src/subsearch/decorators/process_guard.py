import ctypes
import functools
import time
from typing import Any, Callable

from subsearch.runtime.config import GUID
from subsearch.runtime.config import session as config_session
from subsearch.runtime.config.defaults import ConfigKey
from subsearch.runtime.logging.events import LogEvent
from subsearch.runtime.logging.logger import log
from subsearch.runtime.models import exceptions
from subsearch.runtime.startup import PERF_COUNTER

ERROR_ALREADY_EXISTS = 183
WAIT_INFINITE = -1


def _create_mutex() -> Any:
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    mutex = kernel32.CreateMutexW(None, False, GUID)

    if ctypes.get_last_error() == ERROR_ALREADY_EXISTS:
        raise exceptions.MultipleInstancesError(GUID)

    return kernel32, mutex


def _wait_for_mutex(kernel32: Any, mutex: Any) -> None:
    kernel32.WaitForSingleObject(mutex, WAIT_INFINITE)
    log.event(LogEvent.GUARD_MUTEX_ACQUIRED, level="debug", guid=GUID)


def _release_mutex(kernel32: Any, mutex: Any) -> None:
    kernel32.ReleaseMutex(mutex)
    log.event(LogEvent.GUARD_MUTEX_RELEASED, level="debug", guid=GUID)


def _log_single_instance_setting() -> None:
    try:
        single_instance = config_session.get_config_session().read(ConfigKey.APPLICATION_SINGLE_INSTANCE)
    except FileNotFoundError, KeyError, TypeError:
        return

    log.event(
        LogEvent.GUARD_SINGLE_INSTANCE,
        level="debug",
        single_instance=single_instance,
    )

    if not single_instance:
        log.event(LogEvent.GUARD_SINGLE_INSTANCE_DISABLED, level="debug")


def _run_with_mutex(func: Callable, *args: Any, **kwargs: Any) -> Any:
    kernel32, mutex = _create_mutex()

    try:
        _wait_for_mutex(kernel32, mutex)
        _log_single_instance_setting()
        return func(*args, **kwargs)
    finally:
        _release_mutex(kernel32, mutex)


def apply_mutex(func: Callable) -> Callable:
    @functools.wraps(func)
    def inner(*args: Any, **kwargs: Any) -> Any:
        log.event(LogEvent.SPINNER, title="Initializing", done_title="Initialized")
        crashed = False
        try:
            return _run_with_mutex(func, *args, **kwargs)
        except BaseException:
            crashed = True
            raise
        finally:
            log.event(LogEvent.SPINNER, title="Finishing up", done_title="Finished up")
            log.end_banner()
            event = LogEvent.PIPELINE_CRASHED if crashed else LogEvent.PIPELINE_FINISHED
            log.event(event, seconds=time.perf_counter() - PERF_COUNTER)

    return inner
