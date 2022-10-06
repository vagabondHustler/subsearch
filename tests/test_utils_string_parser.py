from src.subsearch.core import BaseInitializer
from src.subsearch.utils import log, raw_config, string_parser

LANGUAGES = raw_config.get_config_key("languages")


def test_str_parser_movie() -> None:
    """
    test so to ensure that the src/subsearch/utils/string_parser.pct_value function returns a with the correct percentage
    """
    movie_1080p = "the.foo.bar.2021.1080p.web.h264-foobar"
    movie_720p = "the.foo.bar.2021.720p.web.h264-foobar"
    show_1080p = "the.foo.bar.s01e01.1080p.web.h264-foobar"
    show_720p = "the.foo.bar.s01e01.720p.web.h264-foobar"
    no_match = "then.fooing.baring.2022.720p.webby.h265-f00bar"

    pct0 = string_parser.get_pct_value(movie_1080p, movie_720p)
    pct1 = string_parser.get_pct_value(show_1080p, show_720p)
    pct2 = string_parser.get_pct_value(movie_1080p, show_1080p)
    pct3 = string_parser.get_pct_value(show_1080p, movie_1080p)
    pct4 = string_parser.get_pct_value(movie_1080p, movie_1080p)
    pct5 = string_parser.get_pct_value(movie_1080p, no_match)

    assert pct0 == 100
    assert pct1 == 100
    assert pct2 == 83
    assert pct3 == 83
    assert pct4 == 100
    assert pct5 == 0


def test_string_parser_movie() -> None:
    """
    test to ensure that the src/subsearch/utils/file_parser.get_parameters function returns the correct parameters for a movie so as to be able to search for subtitles
    """

    filename = "the.foo.bar.2021.1080p.web.h264-foobar"
    base = BaseInitializer()
    fsd = string_parser.get_file_search_data(filename, "000000000000000000")

    assert fsd.title == "the foo bar"
    assert fsd.year == 2021
    assert fsd.season == "N/A"
    assert fsd.season_ordinal == "N/A"
    assert fsd.episode == "N/A"
    assert fsd.episode_ordinal == "N/A"
    assert fsd.series is False
    assert fsd.release == "the.foo.bar.2021.1080p.web.h264-foobar"
    assert fsd.group == "foobar"
    assert fsd.file_hash == "000000000000000000"


def test_string_parser_show() -> None:
    """
    test to ensure that the src/subsearch/utils/file_parser.get_parameters function returns the correct parameters for a show so as to be able to search for subtitles
    """
    filename = "the.foo.bar.s01e01.1080p.web.h264-foobar"
    base = BaseInitializer()
    fsd = string_parser.get_file_search_data(filename, "000000000000000000")

    assert fsd.title == "the foo bar"
    assert fsd.year == 0
    assert fsd.season == "01"
    assert fsd.season_ordinal == "first"
    assert fsd.episode == "01"
    assert fsd.episode_ordinal == "first"
    assert fsd.series is True
    assert fsd.release == "the.foo.bar.s01e01.1080p.web.h264-foobar"
    assert fsd.group == "foobar"
    assert fsd.file_hash == "000000000000000000"


def test_string_parser_bad_filename() -> None:
    filename = "the foo bar 1080p web h264"
    fsd = string_parser.get_file_search_data(filename, "000000000000000000")

    assert fsd.title == "the foo bar 1080p web h264"
    assert fsd.year == 0
    assert fsd.season == "N/A"
    assert fsd.season_ordinal == "N/A"
    assert fsd.episode == "N/A"
    assert fsd.episode_ordinal == "N/A"
    assert fsd.series is False
    assert fsd.release == "the foo bar 1080p web h264"
    assert fsd.group == "the foo bar 1080p web h264"
    assert fsd.file_hash == "000000000000000000"


def test_provider_urls_movie():
    base = BaseInitializer()
    filename = "the.foo.bar.2021.1080p.web.h264-foobar"
    fsd = string_parser.get_file_search_data(filename, "000000000000000000")
    pud = string_parser.get_provider_urls("000000000000000000", base.user_data, fsd)

    assert pud.subscene == "https://subscene.com/subtitles/searchbytitle?query=the%20foo%20bar%20(2021)"
    assert (
        pud.opensubtitles
        == "https://www.opensubtitles.org/en/search/sublanguageid-eng/searchonlymovies-on/moviename-the%20foo%20bar%20(2021)/rss_2_00"
    )
    assert pud.opensubtitles_hash == "https://www.opensubtitles.org/en/search/sublanguageid-eng/moviehash-000000000000000000"
    assert pud.yifysubtitles == "N/A"


def test_provider_urls_series():
    base = BaseInitializer()
    filename = "the.foo.bar.s01e01.1080p.web.h264-foobar"
    fsd = string_parser.get_file_search_data(filename, "000000000000000000")
    pud = string_parser.get_provider_urls("000000000000000000", base.user_data, fsd)

    assert pud.subscene == "https://subscene.com/subtitles/searchbytitle?query=the%20foo%20bar%20-%20first%20season"
    assert (
        pud.opensubtitles
        == "https://www.opensubtitles.org/en/search/sublanguageid-eng/searchonlytvseries-on/season-01/episode-01/moviename-the%20foo%20bar/rss_2_00"
    )
    assert pud.opensubtitles_hash == "https://www.opensubtitles.org/en/search/sublanguageid-eng/moviehash-000000000000000000"
    assert pud.yifysubtitles == "N/A"


def test_imdb_tt_id():
    tt_id = string_parser.find_imdb_tt_id("Arctic", 2019)
    assert tt_id == "tt6820256"
