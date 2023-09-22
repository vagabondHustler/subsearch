import pytest

from subsearch.data.constants import FILE_PATHS
from subsearch.utils import io_toml, string_parser
from subsearch.utils.decorators import CallCondition
from tests import constants_test


class FakeSubsearchCore:
    def __init__(self):
        self.file_exist = True
        self.only_foreign_parts = False
        self.app_config = io_toml.get_app_config(FILE_PATHS.config)
        self.release_data = string_parser.get_release_data(constants_test.FAKE_VIDEO_FILE_MOVIE.filename)
        self.provider_urls = constants_test.FAKE_PROVIDER_URLS
        self.accepted_subtitles = []
        self.rejected_subtitles = []
        self.subtitles_found = 0


@pytest.fixture
def fake_subsearch_core():
    cls = FakeSubsearchCore()
    return cls


def test_conditions_opensubtitles(fake_subsearch_core: FakeSubsearchCore):
    fake_subsearch_core.app_config.providers["opensubtitles_hash"] = False
    result = CallCondition.conditions(cls=fake_subsearch_core, function="opensubtitles")
    assert result is True

    fake_subsearch_core.app_config.providers["opensubtitles_hash"] = False
    fake_subsearch_core.app_config.providers["opensubtitles_site"] = False
    result = CallCondition.conditions(cls=fake_subsearch_core, function="opensubtitles")
    assert result is False


def test_conditions_subscene(fake_subsearch_core: FakeSubsearchCore):
    result = CallCondition.conditions(cls=fake_subsearch_core, function="subscene")
    assert result is True

    fake_subsearch_core.app_config.providers["subscene_site"] = False
    result = CallCondition.conditions(cls=fake_subsearch_core, function="subscene")
    assert result is False


def test_conditions_yifysubtitles(fake_subsearch_core: FakeSubsearchCore):
    fake_subsearch_core.only_foreign_parts = True
    fake_subsearch_core.release_data.tvseries = True
    fake_subsearch_core.provider_urls.yifysubtitles = ""
    fake_subsearch_core.app_config.providers["yifysubtitles_site"] = True
    result = CallCondition.conditions(cls=fake_subsearch_core, function="yifysubtitles")
    assert result is False

    fake_subsearch_core.only_foreign_parts = False
    fake_subsearch_core.release_data.tvseries = False
    fake_subsearch_core.provider_urls.yifysubtitles = "fake_url"
    result = CallCondition.conditions(cls=fake_subsearch_core, function="yifysubtitles")
    assert result is True


def test_conditions_download_files(fake_subsearch_core: FakeSubsearchCore):
    fake_subsearch_core.accepted_subtitles = ["subtitle1", "subtitle2"]
    result = CallCondition.conditions(cls=fake_subsearch_core, function="download_files")
    assert result is True


def test_conditions_manual_download(fake_subsearch_core: FakeSubsearchCore):
    fake_subsearch_core.accepted_subtitles = []
    fake_subsearch_core.rejected_subtitles = ["subtitle1"]
    fake_subsearch_core.app_config.manual_download_on_fail = True
    result = CallCondition.conditions(cls=fake_subsearch_core, function="manual_download")
    assert result is True

    fake_subsearch_core.app_config.manual_download_on_fail = False
    result = CallCondition.conditions(cls=fake_subsearch_core, function="manual_download")
    assert result is False


def test_conditions_extract_files(fake_subsearch_core: FakeSubsearchCore):
    fake_subsearch_core.accepted_subtitles = []
    fake_subsearch_core.rejected_subtitles = ["subtitle1"]
    result = CallCondition.conditions(cls=fake_subsearch_core, function="extract_files")
    assert result is False

    fake_subsearch_core.accepted_subtitles = ["subtitle1", "subtitle2"]
    result = CallCondition.conditions(cls=fake_subsearch_core, function="extract_files")
    assert result is True


def test_conditions_subtitle_rename(fake_subsearch_core: FakeSubsearchCore):
    fake_subsearch_core.subtitles_found = 2
    fake_subsearch_core.app_config.subtitle_post_processing["rename"] = True
    result = CallCondition.conditions(cls=fake_subsearch_core, function="subtitle_rename")
    assert result is True

    fake_subsearch_core.app_config.subtitle_post_processing["rename"] = False
    result = CallCondition.conditions(cls=fake_subsearch_core, function="subtitle_rename")
    assert result is False


def test_conditions_subtitle_move_best(fake_subsearch_core: FakeSubsearchCore):
    fake_subsearch_core.subtitles_found = 2
    fake_subsearch_core.app_config.subtitle_post_processing["move_best"] = True
    result = CallCondition.conditions(cls=fake_subsearch_core, function="subtitle_move_best")
    assert result is True

    fake_subsearch_core.app_config.subtitle_post_processing["move_all"] = True
    result = CallCondition.conditions(cls=fake_subsearch_core, function="subtitle_move_best")
    assert result is False

    fake_subsearch_core.app_config.subtitle_post_processing["move_all"] = False
    fake_subsearch_core.app_config.subtitle_post_processing["move_best"] = False
    result = CallCondition.conditions(cls=fake_subsearch_core, function="subtitle_move_best")
    assert result is False


def test_conditions_subtitle_move_all(fake_subsearch_core: FakeSubsearchCore):
    fake_subsearch_core.subtitles_found = 2
    fake_subsearch_core.app_config.subtitle_post_processing["move_all"] = True
    result = CallCondition.conditions(cls=fake_subsearch_core, function="subtitle_move_all")
    assert result is True

    fake_subsearch_core.app_config.subtitle_post_processing["move_all"] = False
    result = CallCondition.conditions(cls=fake_subsearch_core, function="subtitle_move_all")
    assert result is False


def test_conditions_summary_notification(fake_subsearch_core: FakeSubsearchCore):
    fake_subsearch_core.app_config.summary_notification = True
    result = CallCondition.conditions(cls=fake_subsearch_core, function="summary_notification")
    assert result is True

    fake_subsearch_core.app_config.summary_notification = False
    result = CallCondition.conditions(cls=fake_subsearch_core, function="summary_notification")
    assert result is False


if __name__ == "__main__":
    pytest.main()
