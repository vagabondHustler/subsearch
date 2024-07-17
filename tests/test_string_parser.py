from subsearch.globals.constants import FILE_PATHS
from subsearch.utils import imdb_lookup, io_toml, string_parser
from tests import globals_test


def test_str_parser_movie() -> None:
    movie_1080p = "the.foo.bar.2021.1080p.web.h264-foobar"
    movie_720p = "the.foo.bar.2021.720p.web.h264-foobar"
    show_1080p = "the.foo.bar.s01e01.1080p.web.h264-foobar"
    show_720p = "the.foo.bar.s01e01.720p.web.h264-foobar"
    no_match = "then.fooing.baring.2022.720p.webby.h265-f00bar"

    pct0 = string_parser.calculate_match(movie_1080p, movie_720p)
    pct1 = string_parser.calculate_match(show_1080p, show_720p)
    pct2 = string_parser.calculate_match(movie_1080p, show_1080p)
    pct3 = string_parser.calculate_match(show_1080p, movie_1080p)
    pct4 = string_parser.calculate_match(movie_1080p, movie_1080p)
    pct5 = string_parser.calculate_match(movie_1080p, no_match)

    assert pct0 == 100
    assert pct1 == 100
    assert pct2 == 83
    assert pct3 == 83
    assert pct4 == 100
    assert pct5 == 0


def test_string_parser_movie() -> None:
    filename = "the.foo.bar.2021.1080p.web.h264-foobar"
    release_data = string_parser.get_release_data(filename)

    assert release_data.title == "the foo bar"
    assert release_data.year == 2021
    assert release_data.season == ""
    assert release_data.season_ordinal == ""
    assert release_data.episode == ""
    assert release_data.episode_ordinal == ""
    assert release_data.tvseries is False
    assert release_data.release == "the.foo.bar.2021.1080p.web.h264-foobar"
    assert release_data.group == "foobar"


def test_string_parser_show() -> None:
    filename = "the.foo.bar.s01e01.1080p.web.h264-foobar"
    release_data = string_parser.get_release_data(filename)

    assert release_data.title == "the foo bar"
    assert release_data.year == 0
    assert release_data.season == "01"
    assert release_data.season_ordinal == "first"
    assert release_data.episode == "01"
    assert release_data.episode_ordinal == "first"
    assert release_data.tvseries is True
    assert release_data.release == "the.foo.bar.s01e01.1080p.web.h264-foobar"
    assert release_data.group == "foobar"


def test_string_parser_bad_filename() -> None:
    filename = "the foo bar 1080p web h264"
    release_data = string_parser.get_release_data(filename)

    assert release_data.title == "the foo bar 1080p web h264"
    assert release_data.year == 0
    assert release_data.season == ""
    assert release_data.season_ordinal == ""
    assert release_data.episode == ""
    assert release_data.episode_ordinal == ""
    assert release_data.tvseries is False
    assert release_data.release == "the foo bar 1080p web h264"
    assert release_data.group == "the foo bar 1080p web h264"


def test_provider_urls_movie(monkeypatch):
    monkeypatch.setattr(string_parser, "VIDEO_FILE", globals_test.FAKE_VIDEO_FILE_MOVIE)
    app_config = io_toml.get_app_config(FILE_PATHS.config)
    filename = globals_test.FAKE_VIDEO_FILE_MOVIE.filename
    release_data = string_parser.get_release_data(filename)
    language_data = io_toml.load_toml_data(FILE_PATHS.language_data)
    create_provider_urls = string_parser.CreateProviderUrls(
        app_config,
        release_data,
        language_data,
    )
    provider_url = create_provider_urls.retrieve_urls()

    assert (
        provider_url.opensubtitles
        == "https://www.opensubtitles.org/en/search/sublanguageid-eng/searchonlymovies-on/moviename-the%20foo%20bar%20(2021)/rss_2_00"
    )
    assert provider_url.opensubtitles_hash == "https://www.opensubtitles.org/en/search/sublanguageid-eng/moviehash-"
    assert provider_url.yifysubtitles == ""


def test_provider_urls_series(monkeypatch):
    monkeypatch.setattr(string_parser, "VIDEO_FILE", globals_test.FAKE_VIDEO_FILE_SERIES)
    app_config = io_toml.get_app_config(FILE_PATHS.config)
    filename = globals_test.FAKE_VIDEO_FILE_SERIES.filename
    release_data = string_parser.get_release_data(filename)
    language_data = io_toml.load_toml_data(FILE_PATHS.language_data)
    create_provider_urls = string_parser.CreateProviderUrls(
        app_config,
        release_data,
        language_data,
    )
    provider_url = create_provider_urls.retrieve_urls()

    assert (
        provider_url.opensubtitles
        == "https://www.opensubtitles.org/en/search/sublanguageid-eng/searchonlytvseries-on/season-01/episode-01/moviename-the%20foo%20bar/rss_2_00"
    )
    assert provider_url.opensubtitles_hash == "https://www.opensubtitles.org/en/search/sublanguageid-eng/moviehash-"
    assert provider_url.yifysubtitles == ""


def test_imdb_movie():
    imdb = imdb_lookup.FindImdbID("Arctic", 2019, False)
    assert imdb.imdb_id == "tt6820256"

def test_imdb_tvseries():
    imdb = imdb_lookup.FindImdbID("Breaking bad", 0, True)
    assert imdb.imdb_id == "tt0903747"
