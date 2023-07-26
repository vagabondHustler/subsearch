import pytest

from subsearch.data.constants import FILE_PATHS
from subsearch.utils import io_toml, string_parser
from subsearch.utils.decorators import CallCondition
from tests import constants_test


class FakeSubsearchCore:
    def __init__(self):
        self.file_exist = True
        self.foreign_only = False
        self.app_config = io_toml.get_app_config(FILE_PATHS.subsearch_config)
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
    fake_subsearch_core.app_config.foreign_only = True
    result = CallCondition.conditions(cls=fake_subsearch_core, function="opensubtitles")
    assert result is False

    fake_subsearch_core.app_config.foreign_only = False
    result = CallCondition.conditions(cls=fake_subsearch_core, function="opensubtitles")
    assert result is True

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
    fake_subsearch_core.foreign_only = True
    fake_subsearch_core.release_data.tvseries = True
    fake_subsearch_core.provider_urls.yifysubtitles = ""
    fake_subsearch_core.app_config.providers["yifysubtitles_site"] = True
    result = CallCondition.conditions(cls=fake_subsearch_core, function="yifysubtitles")
    assert result is False

    fake_subsearch_core.foreign_only = False
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


def test_conditions_autoload_rename(fake_subsearch_core: FakeSubsearchCore):
    fake_subsearch_core.subtitles_found = 2
    fake_subsearch_core.app_config.autoload_rename = True
    result = CallCondition.conditions(cls=fake_subsearch_core, function="autoload_rename")
    assert result is True

    fake_subsearch_core.app_config.autoload_rename = False
    result = CallCondition.conditions(cls=fake_subsearch_core, function="autoload_rename")
    assert result is False


def test_conditions_autoload_move(fake_subsearch_core: FakeSubsearchCore):
    fake_subsearch_core.subtitles_found = 2
    fake_subsearch_core.app_config.autoload_move = True
    result = CallCondition.conditions(cls=fake_subsearch_core, function="autoload_move")
    assert result is True

    fake_subsearch_core.app_config.autoload_move = False
    result = CallCondition.conditions(cls=fake_subsearch_core, function="autoload_move")
    assert result is False


def test_conditions_summary_toast(fake_subsearch_core: FakeSubsearchCore):
    fake_subsearch_core.app_config.toast_summary = True
    result = CallCondition.conditions(cls=fake_subsearch_core, function="summary_toast")
    assert result is True

    fake_subsearch_core.app_config.toast_summary = False
    result = CallCondition.conditions(cls=fake_subsearch_core, function="summary_toast")
    assert result is False


if __name__ == "__main__":
    pytest.main()
