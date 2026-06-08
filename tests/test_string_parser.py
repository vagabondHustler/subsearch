from subsearch.runtime.config.constants import FILE_PATHS
from subsearch.io import toml_file
from subsearch.parsing import release_parser
from tests import fixture_data


def test_str_parser_movie() -> None:
    movie_1080p = "the.foo.bar.2021.1080p.web.h264-foobar"
    movie_720p = "the.foo.bar.2021.720p.web.h264-foobar"
    show_1080p = "the.foo.bar.s01e01.1080p.web.h264-foobar"
    show_720p = "the.foo.bar.s01e01.720p.web.h264-foobar"
    no_match = "then.fooing.baring.2022.720p.webby.h265-f00bar"

    # resolution-only difference normalises to exact match
    assert release_parser.calculate_match(movie_1080p, movie_720p) == 100
    assert release_parser.calculate_match(show_1080p, show_720p) == 100
    # identical input
    assert release_parser.calculate_match(movie_1080p, movie_1080p) == 100
    # movie vs show: same title/group/source, one side missing year or SE — no penalty
    assert release_parser.calculate_match(movie_1080p, show_1080p) == 100
    assert release_parser.calculate_match(show_1080p, movie_1080p) == 100
    # completely different titles, groups, and years
    assert release_parser.calculate_match(movie_1080p, no_match) == 0


def test_str_parser_year_mismatch_collapses_score() -> None:
    movie_2021 = "the.foo.bar.2021.1080p.web.h264-foobar"
    movie_1993 = "the.foo.bar.1993.1080p.web.h264-foobar"
    assert release_parser.calculate_match(movie_2021, movie_1993) <= 10


def test_str_parser_season_episode_mismatch_collapses_score() -> None:
    show_s01e01 = "the.foo.bar.s01e01.1080p.web.h264-foobar"
    show_s01e02 = "the.foo.bar.s01e02.1080p.web.h264-foobar"
    assert release_parser.calculate_match(show_s01e01, show_s01e02) <= 10


def test_str_parser_group_boosts_score() -> None:
    same_group = "the.foo.bar.2021.1080p.web.h264-foobar"
    diff_group = "the.foo.bar.2021.1080p.web.h264-othgrp"
    score_same = release_parser.calculate_match(same_group, same_group)
    score_diff = release_parser.calculate_match(same_group, diff_group)
    assert score_same > score_diff


def test_str_parser_4k_stripped_like_2160p() -> None:
    release_2160p = "the.foo.bar.2021.2160p.web.h264-foobar"
    release_4k = "the.foo.bar.2021.4k.web.h264-foobar"
    assert release_parser.calculate_match(release_2160p, release_4k) == 100


def test_string_parser_movie() -> None:
    filename = "the.foo.bar.2021.1080p.web.h264-foobar"
    release_data = release_parser.get_release_data(filename)

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
    release_data = release_parser.get_release_data(filename)

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
    release_data = release_parser.get_release_data(filename)

    assert release_data.title == "the foo bar 1080p web h264"
    assert release_data.year == 0
    assert release_data.season == ""
    assert release_data.season_ordinal == ""
    assert release_data.episode == ""
    assert release_data.episode_ordinal == ""
    assert release_data.tvseries is False
    assert release_data.release == "the foo bar 1080p web h264"
    assert release_data.group == "the foo bar 1080p web h264"


def test_provider_urls_movie(monkeypatch) -> None:
    monkeypatch.setattr(release_parser, "VIDEO_FILE", fixture_data.FAKE_VIDEO_FILE_MOVIE)
    app_config = toml_file.get_app_config(FILE_PATHS.config)
    filename = fixture_data.FAKE_VIDEO_FILE_MOVIE.filename
    release_data = release_parser.get_release_data(filename)
    language_data = toml_file.load_toml_data(FILE_PATHS.subtitle_languages)
    create_provider_urls = release_parser.CreateProviderUrls(
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


def test_provider_urls_series(monkeypatch) -> None:
    monkeypatch.setattr(release_parser, "VIDEO_FILE", fixture_data.FAKE_VIDEO_FILE_SERIES)
    app_config = toml_file.get_app_config(FILE_PATHS.config)
    filename = fixture_data.FAKE_VIDEO_FILE_SERIES.filename
    release_data = release_parser.get_release_data(filename)
    language_data = toml_file.load_toml_data(FILE_PATHS.subtitle_languages)
    create_provider_urls = release_parser.CreateProviderUrls(
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
