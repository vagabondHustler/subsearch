from typing import Any, Callable

enable_system_tray: bool


def check_option_disabled(func) -> Callable[..., Any]:
    def wrapper(self, event, *args, **kwargs) -> Any:
        btn = event.widget
        if btn.instate(["disabled"]):
            return None
        return func(self, event, *args, **kwargs)

    return wrapper


def system_tray_conditions(func) -> Callable[..., Any]:
    def wrapper(*args, **kwargs) -> Any:
        if enable_system_tray:
            return func(*args, **kwargs)

    return wrapper
