from selectolax.parser import HTMLParser

from subsearch.io.language_data import load_language_data
from subsearch.parsing import release_parser
from subsearch.providers import tvsubtitles
from subsearch.runtime.config import session as config_session
from subsearch.runtime.config.defaults import get_default_app_config
from subsearch.runtime.models import ProviderDiagnosticStatus
from tests import fixture_data


def _build_tvsubtitles(
    filename: str = fixture_data.FAKE_SEARCH_SUBJECT_SERIES.search_term,
    selected_language: str = "english",
) -> tvsubtitles.TvSubtitles:
    app_config = config_session.get_app_config_from_data(get_default_app_config())
    app_config.selected_language = selected_language
    language_data = load_language_data()
    release_data = release_parser.get_release_info(filename)
    return tvsubtitles.TvSubtitles(
        release_data=release_data,
        app_config=app_config,
        provider_urls=fixture_data.FAKE_PROVIDER_URLS,
        language_data=language_data,
        filename=filename,
    )


def test_movie_release_returns_ok_without_searching() -> None:
    scraper = _build_tvsubtitles(fixture_data.FAKE_SEARCH_SUBJECT_MOVIE.search_term)
    assert scraper.get_subtitles() is ProviderDiagnosticStatus.OK


def test_matching_show_id_strips_year_suffix_and_matches_title() -> None:
    scraper = _build_tvsubtitles()
    tree = HTMLParser(
        "<html>"
        "<a href='/tvshow-99.html'>Some Other Show (2010-2014)</a>"
        "<a href='/tvshow-42.html'>The Foo Bar (2019-2021)</a>"
        "</html>"
    )
    assert scraper._matching_show_id(tree) == "42"


def test_matching_episode_id_matches_season_and_episode() -> None:
    scraper = _build_tvsubtitles()
    tree = HTMLParser(
        "<table>"
        "<tr><td>1x02</td><td><a href='episode-100.html'>wrong episode</a></td></tr>"
        "<tr><td>1x01</td><td><a href='episode-200.html'>right episode</a></td></tr>"
        "</table>"
    )
    assert scraper._matching_episode_id(tree) == "200"


def test_collect_subtitles_reads_release_name_and_builds_download_url(monkeypatch) -> None:
    scraper = _build_tvsubtitles()
    captured: list[tuple[str, str, dict[str, str]]] = []
    monkeypatch.setattr(
        scraper, "prepare_subtitle", lambda *args, **kwargs: captured.append((args[1], args[2], args[4]))
    )

    episode_tree = HTMLParser(
        "<html>"
        "<a href='/subtitle-225955.html'>"
        "<div class='subtitlen'><h5>Breaking Bad 5x06 (HDTV.EVOLVE)</h5></div>"
        "</a>"
        "</html>"
    )
    scraper._collect_subtitles(episode_tree)

    assert captured == [
        (
            "Breaking Bad 5x06 (HDTV.EVOLVE)",
            "https://www.tvsubtitles.net/download-225955.html",
            {"Referer": "https://www.tvsubtitles.net/subtitle-225955.html"},
        )
    ]


def test_language_code_uses_tvsubtitles_override() -> None:
    scraper = _build_tvsubtitles()
    scraper.app_config.selected_language = "czech"
    scraper.language_data = {"czech": {"two_letter_code": "cs", "tvsubtitles_code": "cz"}}
    assert scraper.language_code == "cz"


def test_language_code_falls_back_to_two_letter_code() -> None:
    scraper = _build_tvsubtitles()
    scraper.app_config.selected_language = "english"
    scraper.language_data = {"english": {"two_letter_code": "en"}}
    assert scraper.language_code == "en"
