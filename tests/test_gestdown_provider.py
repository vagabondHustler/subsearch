from subsearch.io.language_data import load_language_data
from subsearch.parsing import release_parser
from subsearch.providers.gestdown import (
    API_BASE_URL,
    Gestdown,
    GestdownApi,
    normalize_show_name,
)
from subsearch.runtime.config import session as config_session
from subsearch.runtime.config.defaults import get_default_app_config
from tests import fixture_data


def _build_gestdown(filename: str = fixture_data.FAKE_SEARCH_SUBJECT_SERIES.search_term) -> Gestdown:
    app_config = config_session.get_app_config_from_data(get_default_app_config())
    app_config.hearing_impaired = True
    app_config.non_hearing_impaired = True
    app_config.selected_language = "english"
    language_data = load_language_data()
    release_data = release_parser.get_release_info(filename)
    return Gestdown(
        release_data=release_data,
        app_config=app_config,
        provider_urls=fixture_data.FAKE_PROVIDER_URLS,
        language_data=language_data,
        filename=filename,
    )


def test_download_url_prepends_base_to_uri() -> None:
    api = GestdownApi()
    assert api.download_url("/subtitles/download/abc") == f"{API_BASE_URL}/subtitles/download/abc"


def test_language_name_uses_full_name() -> None:
    provider = _build_gestdown()
    assert provider._language_name == "English"


def test_skip_subtitle_rejects_wrong_language() -> None:
    provider = _build_gestdown()
    subtitle = {"downloadUri": "/x", "version": "x", "language": "Spanish", "hearingImpaired": False}
    assert provider._skip_reason(subtitle) == "language"


def test_skip_subtitle_accepts_matching() -> None:
    provider = _build_gestdown()
    subtitle = {"downloadUri": "/x", "version": "x", "language": "English", "hearingImpaired": False}
    assert provider._skip_reason(subtitle) == ""


def test_skip_subtitle_missing_keys_is_malformed() -> None:
    provider = _build_gestdown()
    assert provider._skip_reason({"downloadUri": "/x"}) == "malformed"


def test_movies_are_skipped() -> None:
    provider = _build_gestdown(fixture_data.FAKE_SEARCH_SUBJECT_MOVIE.search_term)
    provider.start_search(flag="site")
    assert not provider.accepted_subtitles
    assert not provider.rejected_subtitles


def test_normalize_handles_punctuation_and_qualifiers() -> None:
    assert normalize_show_name("The Office (US)") == "the office"
    assert normalize_show_name("Marvel's Daredevil") == "marvels daredevil"
    assert normalize_show_name("Breaking Bad") == "breaking bad"


def test_select_show_prefers_canonical_over_spinoff() -> None:
    provider = _build_gestdown("breaking.bad.s01e01.1080p.web.h264-foobar")
    shows = [
        {"id": "main", "name": "Breaking Bad", "nbSeasons": 5, "seasons": [1, 2, 3, 4, 5]},
        {"id": "spinoff", "name": "Breaking Bad Minisodes", "nbSeasons": 1, "seasons": [1]},
    ]
    chosen = provider._select_show(shows, normalize_show_name(provider.release_data.title))
    assert chosen is not None and chosen["id"] == "main"


def test_select_show_returns_none_without_match() -> None:
    provider = _build_gestdown("breaking.bad.s01e01.1080p.web.h264-foobar")
    shows = [{"id": "x", "name": "Some Other Show", "nbSeasons": 1, "seasons": [1]}]
    assert provider._select_show(shows, normalize_show_name(provider.release_data.title)) is None
