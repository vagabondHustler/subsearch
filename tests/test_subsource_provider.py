import pytest

from subsearch.io import toml_file
from subsearch.parsing import release_parser
from subsearch.providers.subsource import API_BASE_URL, Subsource, SubsourceApi
from subsearch.runtime.config.constants import FILE_PATHS
from subsearch.runtime.models.exceptions import MissingApiKey
from subsearch.runtime.models.model import ProviderHealth
from tests import fixture_data


def _build_subsource(api_key: str, filename: str = fixture_data.FAKE_VIDEO_FILE_MOVIE.filename) -> Subsource:
    app_config = toml_file.get_app_config(FILE_PATHS.config)
    app_config.subsource_api_key = api_key
    app_config.hearing_impaired = True
    app_config.non_hearing_impaired = True
    app_config.selected_language = "english"
    language_data = toml_file.load_toml_data(FILE_PATHS.subtitle_languages)
    release_data = release_parser.get_release_data(filename)
    return Subsource(
        release_data=release_data,
        app_config=app_config,
        provider_urls=fixture_data.FAKE_PROVIDER_URLS,
        language_data=language_data,
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
    assert provider.reported_health[0].health is ProviderHealth.NO_RESPONSE


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
