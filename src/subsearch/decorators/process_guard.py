import ctypes
import functools
import threading
import traceback
from typing import Any, Callable

from subsearch.runtime.config import GUID
from subsearch.runtime.config import session as config_session
from subsearch.runtime.config.defaults import ConfigKey
from subsearch.runtime.models import exceptions
from subsearch.runtime.recorder import LogLevel, capture, flush_crash, phase

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
    capture(f"Mutex acquired: {GUID}", level=LogLevel.DEBUG)


def _release_mutex(kernel32: Any, mutex: Any) -> None:
    kernel32.ReleaseMutex(mutex)
    capture(f"Mutex released: {GUID}", level=LogLevel.DEBUG)


def _log_single_instance_setting() -> None:
    try:
        single_instance = config_session.get_config_session().read(ConfigKey.APPLICATION_SINGLE_INSTANCE)
    except FileNotFoundError, KeyError, TypeError:
        return

    capture(f"Single-instance enforcement: {single_instance}", level=LogLevel.DEBUG)

    if not single_instance:
        capture("Single-instance disabled, skipping mutex", level=LogLevel.DEBUG)


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
        phase("Initializing")
        crashed = False
        try:
            return _run_with_mutex(func, *args, **kwargs)
        except BaseException:
            crashed = True
            flush_crash(threading.current_thread().name, traceback.format_exc())
            raise
        finally:
            if crashed:
                capture("Exited following an unhandled exception", level=LogLevel.WARNING)

    return inner
