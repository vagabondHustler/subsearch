import pytest

from subsearch.core.bootstrap import Bootstrap
from subsearch.runtime.models.model import AppMode


def make_bootstrap(app_mode: AppMode) -> Bootstrap:
    bootstrap = Bootstrap.__new__(Bootstrap)
    bootstrap.app_mode = app_mode
    return bootstrap


def test_gui_may_open_when_settings_mode():
    assert make_bootstrap(AppMode.SETTINGS).gui_may_open is True


def test_gui_may_open_when_search_manual():
    assert make_bootstrap(AppMode.SEARCH_MANUAL).gui_may_open is True


def test_gui_may_open_when_search_hybrid():
    assert make_bootstrap(AppMode.SEARCH_HYBRID).gui_may_open is True


def test_gui_may_open_when_dev_mode():
    assert make_bootstrap(AppMode.DEV).gui_may_open is True


def test_gui_may_not_open_for_automatic_mode():
    assert make_bootstrap(AppMode.SEARCH_AUTOMATIC).gui_may_open is False


if __name__ == "__main__":
    pytest.main()
