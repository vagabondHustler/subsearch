import functools
from typing import Any, Callable

from subsearch.runtime.logging.events import LogEvent
from subsearch.runtime.logging.logger import log


def run_if_conditions_met(func) -> Callable[..., Any]:

    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        instance = args[0]
        class_name = type(instance).__name__
        qualified_name = f"{class_name}.{func.__name__}"
        if not instance.call_conditions.conditions_met(func.__name__):
            log.event(LogEvent.GUARD_STEP_SKIPPED, level="debug", qualified_name=qualified_name)
            return None
        log.event(LogEvent.GUARD_STEP_CALLED, level="debug", qualified_name=qualified_name)
        return func(*args, **kwargs)

    return wrapper
