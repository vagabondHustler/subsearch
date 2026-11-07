from types import SimpleNamespace

import pytest

from subsearch.core.bootstrap import Bootstrap
from subsearch.runtime.models import AppMode


def make_bootstrap(app_mode: AppMode, ui_visibility: str = "attention_required") -> Bootstrap:
    bootstrap = Bootstrap.__new__(Bootstrap)
    bootstrap.app_mode = app_mode
    bootstrap.app_config = SimpleNamespace(ui_visibility=ui_visibility)  # type: ignore[assignment]
    return bootstrap


def test_gui_may_open_when_settings_mode():
    assert make_bootstrap(AppMode.SETTINGS).ui_may_open is True


def test_gui_may_open_when_search_manual():
    assert make_bootstrap(AppMode.SEARCH_MANUAL).ui_may_open is True


def test_gui_may_open_for_automatic_always():
    assert make_bootstrap(AppMode.SEARCH_AUTOMATIC, "always").ui_may_open is True


def test_gui_may_open_for_automatic_attention_required():
    assert make_bootstrap(AppMode.SEARCH_AUTOMATIC, "attention_required").ui_may_open is True


def test_gui_may_not_open_for_automatic_never():
    assert make_bootstrap(AppMode.SEARCH_AUTOMATIC, "never").ui_may_open is False


if __name__ == "__main__":
    pytest.main()
