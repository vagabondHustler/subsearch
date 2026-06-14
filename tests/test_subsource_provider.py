import pytest

from subsearch.io.language_data import load_language_data
from subsearch.parsing import release_parser
from subsearch.providers.subsource import API_BASE_URL, Subsource, SubsourceApi
from subsearch.runtime.config import session as config_session
from subsearch.runtime.config.defaults import get_default_app_config
from subsearch.runtime.models import ProviderDiagnosticStatus
from subsearch.runtime.models.exceptions import MissingApiKey
from tests import fixture_data


def _build_subsource(api_key: str, filename: str = fixture_data.FAKE_SEARCH_SUBJECT_MOVIE.search_term) -> Subsource:
    app_config = config_session.get_app_config_from_data(get_default_app_config())
    app_config.subsource_api_key = api_key
    app_config.hearing_impaired = True
    app_config.non_hearing_impaired = True
    app_config.selected_language = "english"
    language_data = load_language_data()
    release_data = release_parser.get_release_info(filename)
    return Subsource(
        release_data=release_data,
        app_config=app_config,
        provider_urls=fixture_data.FAKE_PROVIDER_URLS,
        language_data=language_data,
        filename=filename,
    )


def test_download_url_is_built_from_subtitle_id() -> None:
    api = SubsourceApi("sk_test")
    assert api.download_url(42) == f"{API_BASE_URL}/subtitles/42/download"


def test_auth_header_uses_x_api_key() -> None:
    api = SubsourceApi("sk_test")
    assert api.auth_headers() == {"X-API-Key": "sk_test"}


def test_missing_key_raises_and_reports_no_response() -> None:
    provider = _build_subsource(api_key="")
    with pytest.raises(MissingApiKey):
        provider.start_search(flag="site")
    assert provider.reported_health[0].diagnostic_status is ProviderDiagnosticStatus.NO_RESPONSE


def test_skip_subtitle_rejects_wrong_language() -> None:
    provider = _build_subsource(api_key="sk_test")
    subtitle = {"subtitleId": 1, "releaseInfo": ["x"], "language": "spanish", "hearingImpaired": False}
    assert provider._skip_reason(subtitle) == "language"


def test_skip_subtitle_accepts_matching() -> None:
    provider = _build_subsource(api_key="sk_test")
    subtitle = {"subtitleId": 1, "releaseInfo": ["x"], "language": "english", "hearingImpaired": False}
    assert provider._skip_reason(subtitle) == ""


def test_skip_subtitle_missing_keys_is_skipped() -> None:
    provider = _build_subsource(api_key="sk_test")
    assert provider._skip_reason({"subtitleId": 1}) == "malformed"


def test_skip_movie_rejects_wrong_title() -> None:
    provider = _build_subsource(api_key="sk_test")
    movie = {"movieId": 1, "type": "movie", "title": "Some Other Film"}
    assert provider._skip_movie(movie) is True
