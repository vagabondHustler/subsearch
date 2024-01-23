import inspect
import pytest

from subsearch.globals.constants import FILE_PATHS
from subsearch.utils import io_toml, string_parser
from subsearch.globals.decorators import _CoreSubsearchFuncCondtitons
from tests import globals_test


class FakeSubsearchCore:
    def __init__(self) -> None:
        self.file_exist = True
        self.only_foreign_parts = False
        self.app_config = io_toml.get_app_config(FILE_PATHS.config)
        self.release_data = string_parser.get_release_data(globals_test.FAKE_VIDEO_FILE_MOVIE.filename)
        self.provider_urls = globals_test.FAKE_PROVIDER_URLS
        self.accepted_subtitles = []
        self.rejected_subtitles = []
        self.downloaded_subtitles = 0
        self.call_func = _CoreSubsearchFuncCondtitons.conditions_met

    @property
    def func_name(self) -> str:
        caller_frame = inspect.stack()[1]
        caller_function_name = inspect.getframeinfo(caller_frame[0]).function
        assert caller_function_name.startswith("test_conditions_") is True
        return caller_function_name.replace("test_conditions_", "")


@pytest.fixture
def fake_cls() -> FakeSubsearchCore:
    return FakeSubsearchCore()


def test_conditions_opensubtitles(fake_cls: FakeSubsearchCore) -> None:
    fake_cls.app_config.providers["opensubtitles_hash"] = False
    assert fake_cls.call_func(cls=fake_cls, func_name=fake_cls.func_name) is True

    fake_cls.app_config.providers["opensubtitles_hash"] = False
    fake_cls.app_config.providers["opensubtitles_site"] = False
    assert fake_cls.call_func(cls=fake_cls, func_name=fake_cls.func_name) is False


def test_conditions_subscene(fake_cls: FakeSubsearchCore) -> None:
    assert fake_cls.call_func(cls=fake_cls, func_name=fake_cls.func_name) is True

    fake_cls.app_config.providers["subscene_site"] = False
    assert fake_cls.call_func(cls=fake_cls, func_name=fake_cls.func_name) is False


def test_conditions_yifysubtitles(fake_cls: FakeSubsearchCore) -> None:
    fake_cls.only_foreign_parts = True
    fake_cls.release_data.tvseries = True
    fake_cls.provider_urls.yifysubtitles = ""
    fake_cls.app_config.providers["yifysubtitles_site"] = True
    assert fake_cls.call_func(cls=fake_cls, func_name=fake_cls.func_name) is False

    fake_cls.only_foreign_parts = False
    fake_cls.release_data.tvseries = False
    fake_cls.provider_urls.yifysubtitles = "fake_url"
    assert fake_cls.call_func(cls=fake_cls, func_name=fake_cls.func_name) is True


def test_conditions_download_files(fake_cls: FakeSubsearchCore) -> None:
    fake_cls.accepted_subtitles = ["subtitle1", "subtitle2"]
    fake_cls.app_config.always_open = False
    fake_cls.app_config.no_automatic_downloads = False
    assert fake_cls.call_func(cls=fake_cls, func_name=fake_cls.func_name) is True
    
    fake_cls.accepted_subtitles = ["subtitle1", "subtitle2"]
    fake_cls.app_config.always_open = True
    fake_cls.app_config.no_automatic_downloads = False
    assert fake_cls.call_func(cls=fake_cls, func_name=fake_cls.func_name) is True


def test_conditions_download_manager(fake_cls: FakeSubsearchCore) -> None:
    fake_cls.accepted_subtitles = []
    fake_cls.rejected_subtitles = ["subtitle1"]
    fake_cls.app_config.open_on_no_matches = True
    fake_cls.app_config.always_open = False
    fake_cls.app_config.no_automatic_downloads = False
    assert fake_cls.call_func(cls=fake_cls, func_name=fake_cls.func_name) is True

    fake_cls.app_config.open_on_no_matches = False
    assert fake_cls.call_func(cls=fake_cls, func_name=fake_cls.func_name) is False

    fake_cls.app_config.open_on_no_matches = False
    fake_cls.app_config.always_open = True
    assert fake_cls.call_func(cls=fake_cls, func_name=fake_cls.func_name) is True

    fake_cls.accepted_subtitles = ["subtitle1"]
    assert fake_cls.call_func(cls=fake_cls, func_name=fake_cls.func_name) is True

    fake_cls.app_config.no_automatic_downloads = True
    fake_cls.rejected_subtitles = []
    assert fake_cls.call_func(cls=fake_cls, func_name=fake_cls.func_name) is True


def test_conditions_extract_files(fake_cls: FakeSubsearchCore) -> None:
    fake_cls.accepted_subtitles = []
    fake_cls.rejected_subtitles = ["subtitle1"]
    assert fake_cls.call_func(cls=fake_cls, func_name=fake_cls.func_name) is False

    fake_cls.accepted_subtitles = ["subtitle1", "subtitle2"]
    assert fake_cls.call_func(cls=fake_cls, func_name=fake_cls.func_name) is True


def test_conditions_subtitle_rename(fake_cls: FakeSubsearchCore) -> None:
    fake_cls.downloaded_subtitles = 2
    fake_cls.app_config.subtitle_post_processing["rename"] = True
    assert fake_cls.call_func(cls=fake_cls, func_name=fake_cls.func_name) is True

    fake_cls.app_config.subtitle_post_processing["rename"] = False
    assert fake_cls.call_func(cls=fake_cls, func_name=fake_cls.func_name) is False


def test_conditions_subtitle_move_best(fake_cls: FakeSubsearchCore) -> None:
    fake_cls.downloaded_subtitles = 2
    fake_cls.app_config.subtitle_post_processing["move_best"] = True
    assert fake_cls.call_func(cls=fake_cls, func_name=fake_cls.func_name) is True

    fake_cls.app_config.subtitle_post_processing["move_all"] = True
    assert fake_cls.call_func(cls=fake_cls, func_name=fake_cls.func_name) is False

    fake_cls.app_config.subtitle_post_processing["move_all"] = False
    fake_cls.app_config.subtitle_post_processing["move_best"] = False
    assert fake_cls.call_func(cls=fake_cls, func_name=fake_cls.func_name) is False


def test_conditions_subtitle_move_all(fake_cls: FakeSubsearchCore) -> None:
    fake_cls.downloaded_subtitles = 2
    fake_cls.app_config.subtitle_post_processing["move_all"] = True
    assert fake_cls.call_func(cls=fake_cls, func_name=fake_cls.func_name) is True

    fake_cls.app_config.subtitle_post_processing["move_all"] = False
    assert fake_cls.call_func(cls=fake_cls, func_name=fake_cls.func_name) is False


def test_conditions_summary_notification(fake_cls: FakeSubsearchCore) -> None:
    fake_cls.app_config.summary_notification = True
    assert fake_cls.call_func(cls=fake_cls, func_name=fake_cls.func_name) is True

    fake_cls.app_config.summary_notification = False
    assert fake_cls.call_func(cls=fake_cls, func_name=fake_cls.func_name) is False


if __name__ == "__main__":
    pytest.main()
