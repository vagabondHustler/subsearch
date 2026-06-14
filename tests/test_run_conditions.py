import inspect

import pytest

from subsearch.core.run_conditions import RunConditions
from subsearch.io.language_data import load_language_data
from subsearch.parsing import release_parser
from subsearch.runtime.config import config_session
from subsearch.runtime.config.factories import get_default_app_config
from subsearch.runtime.models import AppMode
from tests import fixture_data


class FakeBootstrap:
    def __init__(self, *args, **kwargs) -> None:
        self.app_mode = AppMode.SEARCH_HYBRID
        self.app_config = config_session.get_app_config_from_data(get_default_app_config())
        self.release_data = release_parser.get_release_info(fixture_data.FAKE_VIDEO_FILE_MOVIE.filename)
        self.provider_urls = fixture_data.FAKE_PROVIDER_URLS
        self.language_data = load_language_data()
        self.accepted_subtitles: list[str] = []
        self.rejected_subtitles: list[str] = []
        self.downloaded_subtitle_archives = 0
        self.extracted_subtitle_archives = 0
        self.call_conditions = RunConditions(self)  # type: ignore[arg-type]

    @property
    def func_name(self) -> str:
        caller_frame = inspect.stack()[1]
        caller_function_name = inspect.getframeinfo(caller_frame[0]).function
        assert caller_function_name.startswith("test_conditions_") is True
        return caller_function_name.replace("test_conditions_", "")


@pytest.fixture
def fake_cls() -> FakeBootstrap:
    return FakeBootstrap()


def test_conditions_opensubtitles(fake_cls: FakeBootstrap) -> None:
    fake_cls.app_config.providers["opensubtitles"] = True
    assert fake_cls.call_conditions.conditions_met(fake_cls.func_name) is True

    fake_cls.app_config.providers["opensubtitles"] = False
    assert fake_cls.call_conditions.conditions_met(fake_cls.func_name) is False


def test_conditions_yifysubtitles(fake_cls: FakeBootstrap) -> None:
    fake_cls.app_config.only_foreign_parts = True
    fake_cls.release_data.tvseries = True
    fake_cls.provider_urls.yifysubtitles = []
    fake_cls.app_config.providers["yifysubtitles_site"] = True
    assert fake_cls.call_conditions.conditions_met(fake_cls.func_name) is False

    fake_cls.app_config.only_foreign_parts = False
    fake_cls.release_data.tvseries = False
    fake_cls.provider_urls.yifysubtitles = ["fake_url"]
    assert fake_cls.call_conditions.conditions_met(fake_cls.func_name) is True


def test_conditions_subsource(fake_cls: FakeBootstrap) -> None:
    fake_cls.app_config.only_foreign_parts = True
    fake_cls.release_data.tvseries = True
    fake_cls.app_config.providers["subsource_site"] = True
    assert fake_cls.call_conditions.conditions_met(fake_cls.func_name) is False

    fake_cls.app_config.only_foreign_parts = False
    assert fake_cls.call_conditions.conditions_met(fake_cls.func_name) is True


def test_conditions_download_files(fake_cls: FakeBootstrap) -> None:
    fake_cls.accepted_subtitles = []
    fake_cls.app_mode = AppMode.SEARCH_AUTOMATIC
    assert fake_cls.call_conditions.conditions_met(fake_cls.func_name) is False

    fake_cls.accepted_subtitles = ["subtitle1", "subtitle2"]
    fake_cls.app_mode = AppMode.SEARCH_HYBRID
    assert fake_cls.call_conditions.conditions_met(fake_cls.func_name) is True

    fake_cls.accepted_subtitles = ["subtitle1", "subtitle2"]
    fake_cls.app_mode = AppMode.SEARCH_AUTOMATIC
    assert fake_cls.call_conditions.conditions_met(fake_cls.func_name) is True

    fake_cls.accepted_subtitles = ["subtitle1", "subtitle2"]
    fake_cls.app_mode = AppMode.SEARCH_MANUAL
    assert fake_cls.call_conditions.conditions_met(fake_cls.func_name) is False


def test_conditions_download_manager(fake_cls: FakeBootstrap) -> None:
    fake_cls.app_mode = AppMode.SEARCH_MANUAL
    assert fake_cls.call_conditions.conditions_met(fake_cls.func_name) is True

    fake_cls.app_mode = AppMode.DEV
    assert fake_cls.call_conditions.conditions_met(fake_cls.func_name) is True

    fake_cls.app_mode = AppMode.SEARCH_HYBRID
    fake_cls.accepted_subtitles = []
    fake_cls.rejected_subtitles = ["subtitle1"]
    assert fake_cls.call_conditions.conditions_met(fake_cls.func_name) is True

    fake_cls.accepted_subtitles = []
    fake_cls.rejected_subtitles = []
    assert fake_cls.call_conditions.conditions_met(fake_cls.func_name) is True

    fake_cls.accepted_subtitles = ["subtitle1"]
    fake_cls.rejected_subtitles = []
    assert fake_cls.call_conditions.conditions_met(fake_cls.func_name) is False

    fake_cls.app_mode = AppMode.SEARCH_AUTOMATIC
    assert fake_cls.call_conditions.conditions_met(fake_cls.func_name) is False


def test_conditions_subtitle_post_processing(fake_cls: FakeBootstrap) -> None:
    fake_cls.app_mode = AppMode.SEARCH_HYBRID
    assert fake_cls.call_conditions.conditions_met(fake_cls.func_name) is True

    fake_cls.app_mode = AppMode.SEARCH_AUTOMATIC
    assert fake_cls.call_conditions.conditions_met(fake_cls.func_name) is True

    fake_cls.app_mode = AppMode.SEARCH_MANUAL
    assert fake_cls.call_conditions.conditions_met(fake_cls.func_name) is False

    fake_cls.app_mode = AppMode.DEV
    assert fake_cls.call_conditions.conditions_met(fake_cls.func_name) is False


def test_conditions_extract_files(fake_cls: FakeBootstrap) -> None:
    fake_cls.downloaded_subtitle_archives = 0
    assert fake_cls.call_conditions.conditions_met(fake_cls.func_name) is False

    fake_cls.accepted_subtitles = ["subtitle1", "subtitle2"]
    fake_cls.downloaded_subtitle_archives = 0
    assert fake_cls.call_conditions.conditions_met(fake_cls.func_name) is False

    fake_cls.accepted_subtitles = ["subtitle1", "subtitle2"]
    fake_cls.downloaded_subtitle_archives = 1
    assert fake_cls.call_conditions.conditions_met(fake_cls.func_name) is True


def test_conditions_subtitle_rename(fake_cls: FakeBootstrap) -> None:
    fake_cls.extracted_subtitle_archives = 2
    fake_cls.app_config.post_processing["rename"] = True
    assert fake_cls.call_conditions.conditions_met(fake_cls.func_name) is True

    fake_cls.app_config.post_processing["rename"] = False
    assert fake_cls.call_conditions.conditions_met(fake_cls.func_name) is False

    fake_cls.app_config.post_processing["rename"] = True
    fake_cls.app_mode = AppMode.SEARCH_MANUAL
    assert fake_cls.call_conditions.conditions_met(fake_cls.func_name) is False


def test_conditions_subtitle_move_best(fake_cls: FakeBootstrap) -> None:
    fake_cls.extracted_subtitle_archives = 1
    fake_cls.app_config.post_processing["move_best"] = True
    assert fake_cls.call_conditions.conditions_met(fake_cls.func_name) is True

    fake_cls.extracted_subtitle_archives = 1
    fake_cls.app_config.post_processing["move_best"] = True
    fake_cls.app_config.post_processing["move_all"] = True
    assert fake_cls.call_conditions.conditions_met(fake_cls.func_name) is False

    fake_cls.extracted_subtitle_archives = 1
    fake_cls.app_config.post_processing["move_all"] = False
    fake_cls.app_config.post_processing["move_best"] = False
    assert fake_cls.call_conditions.conditions_met(fake_cls.func_name) is False

    fake_cls.extracted_subtitle_archives = 0
    fake_cls.app_config.post_processing["move_all"] = True
    assert fake_cls.call_conditions.conditions_met(fake_cls.func_name) is False

    fake_cls.extracted_subtitle_archives = 0
    fake_cls.app_config.post_processing["move_best"] = True
    assert fake_cls.call_conditions.conditions_met(fake_cls.func_name) is False

    fake_cls.extracted_subtitle_archives = 0
    fake_cls.app_config.post_processing["move_best"] = True
    fake_cls.app_config.post_processing["open_on_no_matches"] = True
    assert fake_cls.call_conditions.conditions_met(fake_cls.func_name) is False

    fake_cls.extracted_subtitle_archives = 1
    fake_cls.app_config.post_processing["move_best"] = True
    fake_cls.app_config.post_processing["move_all"] = False
    fake_cls.app_mode = AppMode.SEARCH_MANUAL
    assert fake_cls.call_conditions.conditions_met(fake_cls.func_name) is False


def test_conditions_subtitle_move_all(fake_cls: FakeBootstrap) -> None:
    fake_cls.extracted_subtitle_archives = 1
    fake_cls.app_config.post_processing["move_all"] = True
    assert fake_cls.call_conditions.conditions_met(fake_cls.func_name) is True

    fake_cls.app_config.post_processing["move_all"] = False
    assert fake_cls.call_conditions.conditions_met(fake_cls.func_name) is False

    fake_cls.app_config.post_processing["move_all"] = True
    fake_cls.app_mode = AppMode.SEARCH_MANUAL
    assert fake_cls.call_conditions.conditions_met(fake_cls.func_name) is False


def test_manually_handle_post_processing_disables_download_and_post_processing(fake_cls: FakeBootstrap) -> None:
    fake_cls.app_mode = AppMode.SEARCH_HYBRID
    fake_cls.accepted_subtitles = ["subtitle1"]
    fake_cls.downloaded_subtitle_archives = 1
    fake_cls.extracted_subtitle_archives = 1
    fake_cls.app_config.post_processing["rename"] = True
    fake_cls.app_config.post_processing["move_best"] = True
    fake_cls.app_config.post_processing["move_all"] = False

    gated_steps = (
        "download_files",
        "subtitle_post_processing",
        "extract_files",
        "subtitle_rename",
        "subtitle_move_best",
    )

    fake_cls.app_config.manually_handle_post_processing = False
    for step in gated_steps:
        assert fake_cls.call_conditions.conditions_met(step) is True, step

    fake_cls.app_config.manually_handle_post_processing = True
    for step in gated_steps:
        assert fake_cls.call_conditions.conditions_met(step) is False, step

    fake_cls.app_config.post_processing["move_best"] = False
    fake_cls.app_config.post_processing["move_all"] = True
    assert fake_cls.call_conditions.conditions_met("subtitle_move_all") is False
    fake_cls.app_config.manually_handle_post_processing = False
    assert fake_cls.call_conditions.conditions_met("subtitle_move_all") is True


def test_unmet_condition_labels_yifysubtitles_without_imdb_match(fake_cls: FakeBootstrap) -> None:
    fake_cls.app_config.only_foreign_parts = False
    fake_cls.release_data.tvseries = False
    fake_cls.provider_urls.yifysubtitles = []
    fake_cls.app_config.providers["yifysubtitles_site"] = True

    assert fake_cls.call_conditions.unmet_condition_labels("yifysubtitles") == ["url_not_empty"]


def test_unmet_condition_labels_empty_when_provider_runs(fake_cls: FakeBootstrap) -> None:
    fake_cls.app_config.providers["opensubtitles"] = True

    assert fake_cls.call_conditions.unmet_condition_labels("opensubtitles") == []


def test_conditions_summary_notification(fake_cls: FakeBootstrap) -> None:
    fake_cls.app_config.summary_notification = True
    assert fake_cls.call_conditions.conditions_met(fake_cls.func_name) is True

    fake_cls.app_config.summary_notification = False
    assert fake_cls.call_conditions.conditions_met(fake_cls.func_name) is False


if __name__ == "__main__":
    pytest.main()
