from typing import cast

import pytest

from subsearch.core.bootstrap import Bootstrap
from subsearch.runtime.models.model import AppConfig, AppMode


class FakeAppConfig:
    def __init__(self, always_open_manager: bool, open_manager_on_no_matches: bool) -> None:
        self.always_open_manager = always_open_manager
        self.open_manager_on_no_matches = open_manager_on_no_matches


def make_bootstrap(app_mode: AppMode, always_open_manager: bool, open_manager_on_no_matches: bool) -> Bootstrap:
    bootstrap = Bootstrap.__new__(Bootstrap)
    bootstrap.app_mode = app_mode
    bootstrap.app_config = cast(AppConfig, FakeAppConfig(always_open_manager, open_manager_on_no_matches))
    return bootstrap


def test_gui_may_open_when_no_video_file():
    bootstrap = make_bootstrap(AppMode.SETTINGS, always_open_manager=False, open_manager_on_no_matches=False)
    assert bootstrap.gui_may_open is True


def test_gui_may_open_when_always_open_manager_enabled():
    bootstrap = make_bootstrap(AppMode.SEARCH, always_open_manager=True, open_manager_on_no_matches=False)
    assert bootstrap.gui_may_open is True


def test_gui_may_open_when_open_manager_on_no_matches_enabled():
    bootstrap = make_bootstrap(AppMode.SEARCH, always_open_manager=False, open_manager_on_no_matches=True)
    assert bootstrap.gui_may_open is True


def test_gui_may_not_open_for_silent_automatic_run():
    bootstrap = make_bootstrap(AppMode.SEARCH, always_open_manager=False, open_manager_on_no_matches=False)
    assert bootstrap.gui_may_open is False


if __name__ == "__main__":
    pytest.main()
