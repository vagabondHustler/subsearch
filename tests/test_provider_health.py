from selectolax.parser import HTMLParser

from subsearch.runtime.constants import FILE_PATHS
from subsearch.runtime.factories import get_default_app_config
from subsearch.runtime.model import ProviderHealth
from subsearch.io import toml_file
from subsearch.parsing import release_parser
from subsearch.providers import opensubtitles, yifysubtitles
from subsearch.providers.provider_helper import combine_provider_health
from subsearch import diagnostics
from tests import fixture_data


def _search_kwargs() -> dict:
    app_config = toml_file.get_app_config(FILE_PATHS.config)
    language_data = toml_file.load_toml_data(FILE_PATHS.subtitle_languages)
    release_data = release_parser.get_release_data(fixture_data.FAKE_VIDEO_FILE_MOVIE.filename)
    return dict(
        release_data=release_data,
        app_config=app_config,
        provider_urls=fixture_data.FAKE_PROVIDER_URLS,
        language_data=language_data,
    )


def test_combine_provider_health_prioritizes_structure_invalid() -> None:
    combined = combine_provider_health(ProviderHealth.OK, ProviderHealth.STRUCTURE_INVALID)
    assert combined is ProviderHealth.STRUCTURE_INVALID


def test_combine_provider_health_all_no_response() -> None:
    combined = combine_provider_health(ProviderHealth.NO_RESPONSE, ProviderHealth.NO_RESPONSE)
    assert combined is ProviderHealth.NO_RESPONSE


def test_combine_provider_health_defaults_to_ok() -> None:
    combined = combine_provider_health(ProviderHealth.OK, ProviderHealth.NO_RESPONSE)
    assert combined is ProviderHealth.OK


def test_opensubtitles_well_formed_with_channel() -> None:
    scraper = opensubtitles.OpenSubtitles(**_search_kwargs())
    tree = HTMLParser("<rss><channel><item></item></channel></rss>")
    assert scraper.response_is_well_formed(tree) is True


def test_opensubtitles_empty_channel_is_well_formed() -> None:
    scraper = opensubtitles.OpenSubtitles(**_search_kwargs())
    tree = HTMLParser("<rss><channel></channel></rss>")
    assert scraper.response_is_well_formed(tree) is True


def test_opensubtitles_missing_channel_is_structure_invalid() -> None:
    scraper = opensubtitles.OpenSubtitles(**_search_kwargs())
    tree = HTMLParser("<html><body>nothing recognizable</body></html>")
    assert scraper.response_is_well_formed(tree) is False


def test_opensubtitles_maintenance_page_is_no_response() -> None:
    scraper = opensubtitles.OpenSubtitles(**_search_kwargs())
    tree = HTMLParser("<pre>Site will be online soon</pre>")
    assert scraper.classify_response(tree) is ProviderHealth.NO_RESPONSE


def test_opensubtitles_database_outage_is_no_response() -> None:
    scraper = opensubtitles.OpenSubtitles(**_search_kwargs())
    tree = HTMLParser("<html><body>CANNOT CONNECT TO DB: error</body></html>")
    assert scraper.classify_response(tree) is ProviderHealth.NO_RESPONSE


def test_opensubtitles_unrecognized_page_is_structure_invalid() -> None:
    scraper = opensubtitles.OpenSubtitles(**_search_kwargs())
    tree = HTMLParser("<html><body>a brand new layout</body></html>")
    assert scraper.classify_response(tree) is ProviderHealth.STRUCTURE_INVALID


def test_opensubtitles_valid_rss_is_ok() -> None:
    scraper = opensubtitles.OpenSubtitles(**_search_kwargs())
    tree = HTMLParser("<rss><channel><item></item></channel></rss>")
    assert scraper.classify_response(tree) is ProviderHealth.OK


def test_yifysubtitles_well_formed_with_table() -> None:
    scraper = yifysubtitles.YifiSubtitles(**_search_kwargs())
    tree = HTMLParser("<html><table><tr></tr></table></html>")
    assert scraper.response_is_well_formed(tree) is True


def test_yifysubtitles_missing_table_is_structure_invalid() -> None:
    scraper = yifysubtitles.YifiSubtitles(**_search_kwargs())
    tree = HTMLParser("<html><body>redesigned page</body></html>")
    assert scraper.response_is_well_formed(tree) is False


def test_providers_due_when_known_good_is_old() -> None:
    config = get_default_app_config()
    config["diagnostics"]["provider_health"]["opensubtitles"] = {
        "last_known_good": "2026-01-01",
        "last_attempt": "2026-05-01",
    }
    config["diagnostics"]["provider_health"]["subsource"] = {
        "last_known_good": "2026-05-01",
        "last_attempt": "2026-06-01",
    }
    app_config = toml_file.get_app_config_from_data(config)
    due = diagnostics.providers_due_for_diagnostic(app_config)
    assert "opensubtitles" in due
    assert "subsource" not in due


def test_provider_never_attempted_is_not_due() -> None:
    config = get_default_app_config()
    app_config = toml_file.get_app_config_from_data(config)
    assert diagnostics.providers_due_for_diagnostic(app_config) == []
