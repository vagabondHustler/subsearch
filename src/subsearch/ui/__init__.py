import contextlib
import io
from typing import Any

__all__ = ["open_settings_window"]

# qfluentwidgets prints a promo banner to stdout on first import. Warm-import it here, while this
# package initializes, so the banner is suppressed no matter which subsearch.ui.* module triggers
# the first import (system tray at bootstrap, the background warmup, or a direct settings-window call).
with contextlib.redirect_stdout(io.StringIO()):
    import qfluentwidgets  # noqa: F401


def __getattr__(name: str) -> Any:
    if name == "open_settings_window":
        from subsearch.ui.entrypoint import open_settings_window

        return open_settings_window
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
