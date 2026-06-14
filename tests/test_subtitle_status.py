from subsearch.io.language_data import load_language_data
from subsearch.parsing import release_parser
from subsearch.providers import provider_helper
from subsearch.runtime.config import session as config_session
from subsearch.runtime.config.defaults import get_default_app_config
from subsearch.runtime.models import Language, Subtitle, SubtitleStatus
from tests import fixture_data


def _build_helper() -> provider_helper.ProviderHelper:
    app_config = config_session.get_app_config_from_data(get_default_app_config())
    app_config.selected_language = "english"
    language_data = load_language_data()
    language = Language(**language_data[app_config.selected_language])
    filename = fixture_data.FAKE_VIDEO_FILE_MOVIE.filename
    release_data = release_parser.get_release_info(filename)
    helper = provider_helper.ProviderHelper(
        release_data=release_data,
        app_config=app_config,
        provider_urls=fixture_data.FAKE_PROVIDER_URLS,
        language_data=language,
        filename=filename,
    )
    helper.provider_name = "testprovider"
    return helper


def test_record_filtered_out_appends_status_and_counts() -> None:
    helper = _build_helper()
    helper.record_filtered_out("testprovider", "Some.Release.spanish", "language")
    helper.record_filtered_out("testprovider", "Some.Release.hi", "hi")
    helper.record_filtered_out("testprovider", "Another.Release.spanish", "language")

    assert len(helper.filtered_subtitles) == 3
    assert all(subtitle.status is SubtitleStatus.FILTERED_OUT for subtitle in helper.filtered_subtitles)
    assert helper.skip_counts == {"language": 2, "hi": 1}


def _downloaded_count(evaluated: list[Subtitle]) -> int:
    downloaded = {
        id(subtitle): subtitle
        for subtitle in evaluated
        if subtitle.status in (SubtitleStatus.AUTO_DOWNLOADED, SubtitleStatus.MANUALLY_DOWNLOADED)
    }
    return len(downloaded)


def _make_subtitle(status: SubtitleStatus) -> Subtitle:
    return Subtitle(
        token_result=95,
        provider_name="testprovider",
        subtitle_name="some.release",
        download_url="http://example/x.zip",
        request_data={},
        status=status,
    )


def test_summary_numerator_does_not_double_count_auto_then_manual() -> None:
    auto = _make_subtitle(SubtitleStatus.AUTO_DOWNLOADED)
    rejected = _make_subtitle(SubtitleStatus.BELOW_THRESHOLD)
    evaluated = [auto, rejected]

    assert _downloaded_count(evaluated) == 1

    # The download manager re-marks the same already-auto-downloaded object as manual.
    auto.status = SubtitleStatus.MANUALLY_DOWNLOADED
    assert _downloaded_count(evaluated) == 1


def test_summary_counts_distinct_downloads() -> None:
    evaluated = [
        _make_subtitle(SubtitleStatus.AUTO_DOWNLOADED),
        _make_subtitle(SubtitleStatus.MANUALLY_DOWNLOADED),
        _make_subtitle(SubtitleStatus.BELOW_THRESHOLD),
        _make_subtitle(SubtitleStatus.DOWNLOAD_FAILED),
    ]
    assert _downloaded_count(evaluated) == 2
