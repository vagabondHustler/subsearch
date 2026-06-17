import contextlib
import io

with contextlib.redirect_stdout(io.StringIO()):
    import qfluentwidgets  # noqa: F401  (suppresses the library's import-time promo banner)

from subsearch.ui.application import open_settings_window

__all__ = ["open_settings_window"]
