from selectolax.parser import HTMLParser

from subsearch.io import toml_file
from subsearch.parsing import release_parser
from subsearch.providers import diagnostics as diagnostics
from subsearch.providers import opensubtitles, yifysubtitles
from subsearch.providers.provider_helper import combine_provider_diagnostic_status
from subsearch.runtime.config.constants import FILE_PATHS
from subsearch.runtime.config.factories import get_default_app_config
from subsearch.runtime.models.model import ProviderDiagnosticStatus
from tests import fixture_data


def _search_kwargs() -> dict:
    app_config = toml_file.get_app_config(FILE_PATHS.config)
    language_data = toml_file.load_toml_data(FILE_PATHS.subtitle_languages)
    release_data = release_parser.get_release_info(fixture_data.FAKE_VIDEO_FILE_MOVIE.filename)
    return dict(
        release_data=release_data,
        app_config=app_config,
        provider_urls=fixture_data.FAKE_PROVIDER_URLS,
        language_data=language_data,
    )


def test_combine_provider_diagnostic_status_prioritizes_structure_invalid() -> None:
    combined = combine_provider_diagnostic_status(
        ProviderDiagnosticStatus.OK, ProviderDiagnosticStatus.STRUCTURE_INVALID
    )
    assert combined is ProviderDiagnosticStatus.STRUCTURE_INVALID


def test_combine_provider_diagnostic_status_all_no_response() -> None:
    combined = combine_provider_diagnostic_status(
        ProviderDiagnosticStatus.NO_RESPONSE, ProviderDiagnosticStatus.NO_RESPONSE
    )
    assert combined is ProviderDiagnosticStatus.NO_RESPONSE


def test_combine_provider_diagnostic_status_defaults_to_ok() -> None:
    combined = combine_provider_diagnostic_status(ProviderDiagnosticStatus.OK, ProviderDiagnosticStatus.NO_RESPONSE)
    assert combined is ProviderDiagnosticStatus.OK


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
    assert scraper.classify_response(tree) is ProviderDiagnosticStatus.NO_RESPONSE


def test_opensubtitles_database_outage_is_no_response() -> None:
    scraper = opensubtitles.OpenSubtitles(**_search_kwargs())
    tree = HTMLParser("<html><body>CANNOT CONNECT TO DB: error</body></html>")
    assert scraper.classify_response(tree) is ProviderDiagnosticStatus.NO_RESPONSE


def test_opensubtitles_unrecognized_page_is_structure_invalid() -> None:
    scraper = opensubtitles.OpenSubtitles(**_search_kwargs())
    tree = HTMLParser("<html><body>a brand new layout</body></html>")
    assert scraper.classify_response(tree) is ProviderDiagnosticStatus.STRUCTURE_INVALID


def test_opensubtitles_valid_rss_is_ok() -> None:
    scraper = opensubtitles.OpenSubtitles(**_search_kwargs())
    tree = HTMLParser("<rss><channel><item></item></channel></rss>")
    assert scraper.classify_response(tree) is ProviderDiagnosticStatus.OK


def test_yifysubtitles_well_formed_with_table() -> None:
    scraper = yifysubtitles.YifySubtitles(**_search_kwargs())
    tree = HTMLParser("<html><table><tr></tr></table></html>")
    assert scraper.response_is_well_formed(tree) is True


def test_yifysubtitles_missing_table_is_structure_invalid() -> None:
    scraper = yifysubtitles.YifySubtitles(**_search_kwargs())
    tree = HTMLParser("<html><body>redesigned page</body></html>")
    assert scraper.response_is_well_formed(tree) is False


def test_yifysubtitles_download_url_follows_responding_mirror(monkeypatch) -> None:
    kwargs = _search_kwargs()
    kwargs["provider_urls"] = type(kwargs["provider_urls"])(
        opensubtitles=["fake_url"],
        opensubtitles_hash=["fake_url"],
        yifysubtitles=[
            "https://yifysubtitles.ch/movie-imdb/tt0000001",
            "https://yifysubtitles.mx/movie-imdb/tt0000001",
        ],
        subsource=["fake_url"],
    )
    scraper = yifysubtitles.YifySubtitles(**kwargs)

    well_formed_row = (
        "<html><table>"
        "<tr><th>head</th></tr>"
        "<tr><td><span class='sub-lang'>english</span></td>"
        "<td><a href='/subtitle/foo-bar'>subtitle foo.bar.2021</a></td></tr>"
        "</table></html>"
    )

    def fake_request(url: str, timeout) -> object | None:
        if url.startswith("https://yifysubtitles.ch"):
            return None
        return HTMLParser(well_formed_row)

    monkeypatch.setattr(yifysubtitles.http, "request_parsed_response", fake_request)
    captured: list[str] = []
    monkeypatch.setattr(scraper, "prepare_subtitle", lambda *args, **kwargs: captured.append(args[2]))

    status = scraper.get_subtitles()
    assert status is ProviderDiagnosticStatus.OK
    assert captured
    assert all(url.startswith("https://yifysubtitles.mx/subtitle/") for url in captured)


def test_yifysubtitles_fallback_past_malformed_mirror(monkeypatch) -> None:
    kwargs = _search_kwargs()
    kwargs["provider_urls"] = type(kwargs["provider_urls"])(
        opensubtitles=["fake_url"],
        opensubtitles_hash=["fake_url"],
        yifysubtitles=[
            "https://yifysubtitles.ch/movie-imdb/tt0000001",
            "https://yifysubtitles.mx/movie-imdb/tt0000001",
        ],
        subsource=["fake_url"],
    )
    scraper = yifysubtitles.YifySubtitles(**kwargs)

    def fake_request(url: str, timeout) -> object:
        if url.startswith("https://yifysubtitles.ch"):
            return HTMLParser("<html><body>captcha</body></html>")
        return HTMLParser("<html><table><tr><th>head</th></tr></table></html>")

    monkeypatch.setattr(yifysubtitles.http, "request_parsed_response", fake_request)
    status = scraper.get_subtitles()
    assert status is ProviderDiagnosticStatus.OK
    assert scraper.download_domain == "https://yifysubtitles.mx"


def test_providers_due_when_failed_attempts_reach_threshold() -> None:
    config = get_default_app_config()
    threshold = config["diagnostics"]["failed_attempts_threshold"]
    config["diagnostics"]["provider_diagnostics"]["opensubtitles"]["failed_attempts"] = threshold
    config["diagnostics"]["provider_diagnostics"]["subsource"]["failed_attempts"] = threshold - 1
    app_config = toml_file.get_app_config_from_data(config)
    due = diagnostics.providers_due_for_diagnostic(app_config)
    assert "opensubtitles" in due
    assert "subsource" not in due


def test_provider_never_attempted_is_not_due() -> None:
    config = get_default_app_config()
    app_config = toml_file.get_app_config_from_data(config)
    assert diagnostics.providers_due_for_diagnostic(app_config) == []
