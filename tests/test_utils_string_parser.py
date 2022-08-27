from src.subsearch.utils import log, string_parser


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
    param = string_parser.get_parameters(filename, None, "English", "en")
    log.tprint(param)
    assert param.url_subscene == "https://subscene.com/subtitles/searchbytitle?query=the%20foo%20bar"
    assert param.url_opensubtitles == "https://www.opensubtitles.org/en/search/sublanguageid-eng/moviehash-None"
    assert param.title == "the foo bar"
    assert param.year == 2021
    assert param.season == "N/A"
    assert param.season_ordinal == "N/A"
    assert param.episode == "N/A"
    assert param.episode_ordinal == "N/A"
    assert param.show_bool is False
    assert param.release == "the.foo.bar.2021.1080p.web.h264-foobar"
    assert param.group == "foobar"
    assert param.file_hash == None


def test_string_parser_show() -> None:
    """
    test to ensure that the src/subsearch/utils/file_parser.get_parameters function returns the correct parameters for a show so as to be able to search for subtitles
    """
    filename = "the.foo.bar.s01e01.1080p.web.h264-foobar"
    param = string_parser.get_parameters(filename, None, "English", "en")
    log.tprint(param)
    assert param.url_subscene == "https://subscene.com/subtitles/searchbytitle?query=the%20foo%20bar%20-%20first%20season"
    assert param.url_opensubtitles == "https://www.opensubtitles.org/en/search/sublanguageid-eng/moviehash-None"
    assert param.title == "the foo bar - first season"
    assert param.year == "N/A"
    assert param.season == "01"
    assert param.season_ordinal == "first"
    assert param.episode == "01"
    assert param.episode_ordinal == "first"
    assert param.show_bool is True
    assert param.release == "the.foo.bar.s01e01.1080p.web.h264-foobar"
    assert param.group == "foobar"
    assert param.file_hash == None


def test_string_parser_bad_filename() -> None:
    filename = "the foo bar 1080p web h264"
    param = string_parser.get_parameters(filename, None, "English", "en")
    log.tprint(param)

    assert param.url_subscene == "https://subscene.com/subtitles/searchbytitle?query=the%20foo%20bar%201080p%20web%20h264"
    assert param.url_opensubtitles == "https://www.opensubtitles.org/en/search/sublanguageid-eng/moviehash-None"
    assert param.title == "the foo bar 1080p web h264"
    assert param.year == "N/A"
    assert param.season == "N/A"
    assert param.season_ordinal == "N/A"
    assert param.episode == "N/A"
    assert param.episode_ordinal == "N/A"
    assert param.show_bool is False
    assert param.release == "the foo bar 1080p web h264"
    assert param.group == "the foo bar 1080p web h264"
    assert param.file_hash == None
