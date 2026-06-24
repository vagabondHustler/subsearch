import functools
from typing import Any, Callable

from subsearch.runtime.recorder import LogLevel, capture


def run_if_conditions_met(func: Callable[..., Any]) -> Callable[..., Any]:
    # The guard's skip/call/explanation lines are diagnostics for the file log
    # only (debug level), never the console. Meaningful skips a user should see
    # are reported explicitly by the step's caller, swallowed by its banner.

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        instance = args[0]
        class_name = type(instance).__name__
        qualified_name = f"{class_name}.{func.__name__}"
        if not instance.call_conditions.conditions_met(func.__name__):
            capture(f"skipped {qualified_name}", level=LogLevel.DEBUG)
            skip_explanation = instance.call_conditions.skip_explanation(func.__name__)
            if skip_explanation is not None:
                capture(skip_explanation, level=LogLevel.DEBUG)
            return None
        capture(f"called {qualified_name}", level=LogLevel.DEBUG)
        return func(*args, **kwargs)

    return wrapper
