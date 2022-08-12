from src.subsearch.utils import file_parser


def test_file_parser_movie() -> None:
    """
    test to ensure that the src/subsearch/utils/file_parser.get_parameters function returns the correct parameters for a movie so as to be able to search for subtitles
    """
    file_name = "the.foo.bar.2021.1080p.web.h264-foobar"
    param = file_parser.get_parameters(file_name, None, "en")
    param_list = [
        param.url_subscene == "https://subscene.com/subtitles/searchbytitle?query=the%20foo%20bar",
        param.url_opensubtitles == "https://www.opensubtitles.org/en/search/sublanguageid-eng/moviename-None",
        param.title == "the foo bar",
        param.year == "2021",
        param.season == "N/A",
        param.season_ordinal == "N/A",
        param.episode == "N/A",
        param.episode_ordinal == "N/A",
        param.tv_series is False,
        param.release == "the.foo.bar.2021.1080p.web.h264-foobar",
        param.group == "foobar",
        param.file_hash == None,
    ]
    for p in param_list:
        assert p


def test_file_parser_show() -> None:
    """
    test to ensure that the src/subsearch/utils/file_parser.get_parameters function returns the correct parameters for a show so as to be able to search for subtitles
    """
    file_name = "the.foo.bar.s01e01.1080p.web.h264-foobar"
    param = file_parser.get_parameters(file_name, None, "en")
    print(param)
    param_list = [
        param.url_subscene == "https://subscene.com/subtitles/searchbytitle?query=the%20foo%20bar%20-%20first%20season",
        param.url_opensubtitles == "https://www.opensubtitles.org/en/search/sublanguageid-eng/moviename-None",
        param.title == "the foo bar - first season",
        param.year == "N/A",
        param.season == "01",
        param.season_ordinal == "first",
        param.episode == "01",
        param.episode_ordinal == "first",
        param.tv_series is True,
        param.release == "the.foo.bar.s01e01.1080p.web.h264-foobar",
        param.group == "foobar",
        param.file_hash == None,
    ]
    for p in param_list:
        assert p
