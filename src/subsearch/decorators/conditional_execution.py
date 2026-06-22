import functools
from typing import Any, Callable

from subsearch.runtime.logging.events import LogEvent
from subsearch.runtime.logging.logger import log


def run_if_conditions_met(func: Callable[..., Any]) -> Callable[..., Any]:

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        instance = args[0]
        class_name = type(instance).__name__
        qualified_name = f"{class_name}.{func.__name__}"
        if not instance.call_conditions.conditions_met(func.__name__):
            log.event(LogEvent.GUARD_STEP_SKIPPED, level="debug", qualified_name=qualified_name)
            skip_explanation = instance.call_conditions.skip_explanation(func.__name__)
            if skip_explanation is not None:
                log.event(LogEvent.PIPELINE_STEP_SKIPPED, message=skip_explanation)
            return None
        log.event(LogEvent.GUARD_STEP_CALLED, level="debug", qualified_name=qualified_name)
        return func(*args, **kwargs)

    return wrapper
