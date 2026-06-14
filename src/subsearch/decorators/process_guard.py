import ctypes
from typing import Any, Callable

from subsearch.runtime.config import GUID
from subsearch.runtime.config import session as config_session
from subsearch.runtime.logging.logger import log
from subsearch.runtime.models import exceptions


def apply_mutex(func: Callable) -> Callable:
    def inner(*args, **kwargs) -> Any:
        log.event("banner", title="Initializing Subsearch")
        try:
            single_instance = config_session.get_config_session().read("application.single_instance")
            log.event("guard.single_instance", level="debug", single_instance=single_instance)
            if not single_instance:
                log.event("guard.single_instance_disabled", level="debug")
                return func()
        except FileNotFoundError:
            pass
        except KeyError:
            pass
        except TypeError:
            pass
        kernel32 = ctypes.WinDLL("kernel32")
        mutex = kernel32.CreateMutexW(None, False, GUID)
        last_error = kernel32.GetLastError()

        if last_error == 183:
            raise exceptions.MultipleInstancesError(GUID)
        try:
            kernel32.WaitForSingleObject(mutex, -1)
            log.event("guard.mutex_acquired", level="debug", guid=GUID)
            return func(*args, **kwargs)
        finally:
            kernel32.ReleaseMutex(mutex)
            log.event("guard.mutex_released", level="debug", guid=GUID)

    return inner
