from src.subsearch.utils import string_parser


def test_file_parser_movie() -> None:
    file_movie = "the.foo.bar.2021.1080p.web.h264-foobar"
    file_show = "the.foo.bar.s01e01.1080p.web.h264-foobar"
    file_fail = "then.fooing.baring.2022.720p.webby.h265-f00bar"

    pct0 = string_parser.pct_value(file_movie, file_show)
    pct1 = string_parser.pct_value(file_show, file_movie)
    pct2 = string_parser.pct_value(file_movie, file_movie)
    pct3 = string_parser.pct_value(file_movie, file_fail)

    assert pct0.percentage == 83
    assert pct1.percentage == 83
    assert pct2.percentage == 100
    assert pct3.percentage == 0
