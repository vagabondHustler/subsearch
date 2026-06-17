import pytest

from subsearch.core.bootstrap import Bootstrap
from subsearch.runtime.models import AppMode


def make_bootstrap(app_mode: AppMode) -> Bootstrap:
    bootstrap = Bootstrap.__new__(Bootstrap)
    bootstrap.app_mode = app_mode
    return bootstrap


def test_gui_may_open_when_settings_mode():
    assert make_bootstrap(AppMode.SETTINGS).ui_may_open is True


def test_gui_may_open_when_search_manual():
    assert make_bootstrap(AppMode.SEARCH_MANUAL).ui_may_open is True


def test_gui_may_open_when_search_hybrid():
    assert make_bootstrap(AppMode.SEARCH_HYBRID).ui_may_open is True


def test_gui_may_not_open_for_automatic_mode():
    assert make_bootstrap(AppMode.SEARCH_AUTOMATIC).ui_may_open is False


if __name__ == "__main__":
    pytest.main()
