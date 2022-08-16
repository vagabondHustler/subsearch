from src.subsearch.utils import file_parser


def test_file_parser_movie() -> None:
    """
    test to ensure that the src/subsearch/utils/file_parser.get_parameters function returns the correct parameters for a movie so as to be able to search for subtitles
    """
    file_name = "the.foo.bar.2021.1080p.web.h264-foobar"
    param = file_parser.get_parameters(file_name, None, "English", "en")
    print(param)
    assert param.url_subscene == "https://subscene.com/subtitles/searchbytitle?query=the%20foo%20bar"
    assert param.url_opensubtitles == "https://www.opensubtitles.org/en/search/sublanguageid-eng/moviename-None"
    assert param.title == "the foo bar"
    assert param.year == "2021"
    assert param.season == "N/A"
    assert param.season_ordinal == "N/A"
    assert param.episode == "N/A"
    assert param.episode_ordinal == "N/A"
    assert param.show_bool is False
    assert param.release == "the.foo.bar.2021.1080p.web.h264-foobar"
    assert param.group == "foobar"
    assert param.file_hash == None


def test_file_parser_show() -> None:
    """
    test to ensure that the src/subsearch/utils/file_parser.get_parameters function returns the correct parameters for a show so as to be able to search for subtitles
    """
    file_name = "the.foo.bar.s01e01.1080p.web.h264-foobar"
    param = file_parser.get_parameters(file_name, None, "English", "en")
    print(param)
    assert param.url_subscene == "https://subscene.com/subtitles/searchbytitle?query=the%20foo%20bar%20-%20first%20season"
    assert param.url_opensubtitles == "https://www.opensubtitles.org/en/search/sublanguageid-eng/moviename-None"
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
