from src.subsearch.utils import string_parser


def test_file_parser_movie() -> None:
    movie_1080p = "the.foo.bar.2021.1080p.web.h264-foobar"
    movie_720p = "the.foo.bar.2021.720p.web.h264-foobar"
    show_1080p = "the.foo.bar.s01e01.1080p.web.h264-foobar"
    show_720p = "the.foo.bar.s01e01.720p.web.h264-foobar"
    no_match = "then.fooing.baring.2022.720p.webby.h265-f00bar"

    pct0 = string_parser.pct_value(file_movie, file_show)
    pct1 = string_parser.pct_value(file_show, file_movie)
    pct2 = string_parser.pct_value(file_movie, file_movie)
    pct3 = string_parser.pct_value(file_movie, file_fail)

    assert pct0.percentage == 83
    assert pct1.percentage == 83
    assert pct2.percentage == 100
    assert pct3.percentage == 0
