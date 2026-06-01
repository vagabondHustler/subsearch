import functools
from typing import Any, Callable


def call_func(func) -> Callable[..., Any]:

    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        instance = args[0]
        if not instance.call_conditions.call_func(func.__name__):
            return None
        return func(*args, **kwargs)

    return wrapper
