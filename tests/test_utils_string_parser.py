from src.subsearch.core import Initializer
from src.subsearch.utils import imdb, raw_config, string_parser

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
    """
    test to ensure that the src/subsearch/utils/file_parser.get_parameters function returns the correct parameters for a movie so as to be able to search for subtitles
    """

    filename = "the.foo.bar.2021.1080p.web.h264-foobar"
    initializer = Initializer()
    release_metadata = string_parser.get_release_metadata(filename, "000000000000000000")

    assert release_metadata.title == "the foo bar"
    assert release_metadata.year == 2021
    assert release_metadata.season == "N/A"
    assert release_metadata.season_ordinal == "N/A"
    assert release_metadata.episode == "N/A"
    assert release_metadata.episode_ordinal == "N/A"
    assert release_metadata.tvseries is False
    assert release_metadata.release == "the.foo.bar.2021.1080p.web.h264-foobar"
    assert release_metadata.group == "foobar"
    assert release_metadata.file_hash == "000000000000000000"


def test_string_parser_show() -> None:
    """
    test to ensure that the src/subsearch/utils/file_parser.get_parameters function returns the correct parameters for a show so as to be able to search for subtitles
    """
    filename = "the.foo.bar.s01e01.1080p.web.h264-foobar"
    initializer = Initializer()
    release_metadata = string_parser.get_release_metadata(filename, "000000000000000000")

    assert release_metadata.title == "the foo bar"
    assert release_metadata.year == 0
    assert release_metadata.season == "01"
    assert release_metadata.season_ordinal == "first"
    assert release_metadata.episode == "01"
    assert release_metadata.episode_ordinal == "first"
    assert release_metadata.tvseries is True
    assert release_metadata.release == "the.foo.bar.s01e01.1080p.web.h264-foobar"
    assert release_metadata.group == "foobar"
    assert release_metadata.file_hash == "000000000000000000"


def test_string_parser_bad_filename() -> None:
    filename = "the foo bar 1080p web h264"
    release_metadata = string_parser.get_release_metadata(filename, "000000000000000000")

    assert release_metadata.title == "the foo bar 1080p web h264"
    assert release_metadata.year == 0
    assert release_metadata.season == "N/A"
    assert release_metadata.season_ordinal == "N/A"
    assert release_metadata.episode == "N/A"
    assert release_metadata.episode_ordinal == "N/A"
    assert release_metadata.tvseries is False
    assert release_metadata.release == "the foo bar 1080p web h264"
    assert release_metadata.group == "the foo bar 1080p web h264"
    assert release_metadata.file_hash == "000000000000000000"


def test_provider_urls_movie():
    initializer = Initializer()
    filename = "the.foo.bar.2021.1080p.web.h264-foobar"
    release_metadata = string_parser.get_release_metadata(filename, "000000000000000000")
    create_provider_urls = string_parser.CreateProviderUrls("000000000000000000", initializer.app_data, release_metadata)
    provider_url = create_provider_urls.retrieve_urls()

    assert provider_url.subscene == "https://subscene.com/subtitles/searchbytitle?query=the%20foo%20bar"
    assert (
        provider_url.opensubtitles
        == "https://www.opensubtitles.org/en/search/sublanguageid-eng/searchonlymovies-on/moviename-the%20foo%20bar%20(2021)/rss_2_00"
    )
    assert (
        provider_url.opensubtitles_hash == "https://www.opensubtitles.org/en/search/sublanguageid-eng/moviehash-000000000000000000"
    )
    assert provider_url.yifysubtitles == "N/A"


def test_provider_urls_series():
    initializer = Initializer()
    filename = "the.foo.bar.s01e01.1080p.web.h264-foobar"
    release_metadata = string_parser.get_release_metadata(filename, "000000000000000000")
    create_provider_urls = string_parser.CreateProviderUrls("000000000000000000", initializer.app_data, release_metadata)
    provider_url = create_provider_urls.retrieve_urls()

    assert provider_url.subscene == "https://subscene.com/subtitles/searchbytitle?query=the%20foo%20bar%20-%20first%20season"
    assert (
        provider_url.opensubtitles
        == "https://www.opensubtitles.org/en/search/sublanguageid-eng/searchonlytvseries-on/season-01/episode-01/moviename-the%20foo%20bar/rss_2_00"
    )
    assert (
        provider_url.opensubtitles_hash == "https://www.opensubtitles.org/en/search/sublanguageid-eng/moviehash-000000000000000000"
    )
    assert provider_url.yifysubtitles == "N/A"


def test_imdb_tt_id():
    tt_id = imdb.FindImdbID("Arctic", 2019).id
    assert tt_id == "tt6820256"
