from src.subsearch.utils import string_parser


def test_file_parser_movie() -> None:
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
