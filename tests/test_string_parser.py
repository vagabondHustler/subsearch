from subsearch.io import toml_file
from subsearch.parsing import release_parser
from subsearch.runtime.config import static_values
from subsearch.runtime.config.constants import FILE_PATHS
from tests import fixture_data


def test_str_parser_movie() -> None:
    movie_1080p = "the.foo.bar.2021.1080p.web.h264-foobar"
    movie_720p = "the.foo.bar.2021.720p.web.h264-foobar"
    show_1080p = "the.foo.bar.s01e01.1080p.web.h264-foobar"
    show_720p = "the.foo.bar.s01e01.720p.web.h264-foobar"
    no_match = "then.fooing.baring.2022.720p.webby.h265-f00bar"

    # resolution-only difference normalises to exact match
    assert release_parser.score_subtitle_tokens(movie_1080p, movie_720p) == 100
    assert release_parser.score_subtitle_tokens(show_1080p, show_720p) == 100
    # identical input
    assert release_parser.score_subtitle_tokens(movie_1080p, movie_1080p) == 100
    # movie vs show: same title/group/source, one side missing year or SE — no penalty
    assert release_parser.score_subtitle_tokens(movie_1080p, show_1080p) == 100
    assert release_parser.score_subtitle_tokens(show_1080p, movie_1080p) == 100
    # completely different titles, groups, and years
    assert release_parser.score_subtitle_tokens(movie_1080p, no_match) <= 5


def test_str_parser_year_mismatch_collapses_score() -> None:
    movie_2021 = "the.foo.bar.2021.1080p.web.h264-foobar"
    movie_1993 = "the.foo.bar.1993.1080p.web.h264-foobar"
    assert release_parser.score_subtitle_tokens(movie_2021, movie_1993) <= 10


def test_str_parser_season_episode_mismatch_collapses_score() -> None:
    show_s01e01 = "the.foo.bar.s01e01.1080p.web.h264-foobar"
    show_s01e02 = "the.foo.bar.s01e02.1080p.web.h264-foobar"
    assert release_parser.score_subtitle_tokens(show_s01e01, show_s01e02) <= 10


def test_str_parser_group_boosts_score() -> None:
    same_group = "the.foo.bar.2021.1080p.web.h264-foobar"
    diff_group = "the.foo.bar.2021.1080p.web.h264-othgrp"
    score_same = release_parser.score_subtitle_tokens(same_group, same_group)
    score_diff = release_parser.score_subtitle_tokens(same_group, diff_group)
    assert score_same > score_diff


def test_str_parser_default_weights_match_passed_defaults() -> None:
    same_group = "the.foo.bar.2021.1080p.web.h264-foobar"
    diff_group = "the.foo.bar.2021.1080p.web.h264-othgrp"
    assert release_parser.score_subtitle_tokens(same_group, diff_group) == release_parser.score_subtitle_tokens(
        same_group, diff_group, static_values.DEFAULT_TOKEN_WEIGHTS, static_values.DEFAULT_TOKEN_MULTIPLIERS
    )


def test_str_parser_title_dominant_weights_raise_source_mismatch_score() -> None:
    base_release = "the.foo.bar.2021.1080p.web.h264-foobar"
    diff_source = "the.foo.bar.2021.1080p.hdtv.h264-foobar"
    title_dominant_weights = {"title": 90, "group": 5, "source": 5}
    default_score = release_parser.score_subtitle_tokens(base_release, diff_source)
    title_dominant_score = release_parser.score_subtitle_tokens(base_release, diff_source, title_dominant_weights)
    assert title_dominant_score > default_score


def test_str_parser_custom_year_multiplier_softens_penalty() -> None:
    movie_2021 = "the.foo.bar.2021.1080p.web.h264-foobar"
    movie_1993 = "the.foo.bar.1993.1080p.web.h264-foobar"
    lenient_weights = {"title": 60, "group": 30, "source": 10}
    lenient_multipliers = {"year": 0, "season_episode": 0, "edition": 0}
    assert release_parser.score_subtitle_tokens(movie_2021, movie_1993, lenient_weights, lenient_multipliers) == 100


def test_str_parser_4k_stripped_like_2160p() -> None:
    release_2160p = "the.foo.bar.2021.2160p.web.h264-foobar"
    release_4k = "the.foo.bar.2021.4k.web.h264-foobar"
    assert release_parser.score_subtitle_tokens(release_2160p, release_4k) == 100


def test_str_parser_audio_codec_stripped() -> None:
    release_dts = "the.foo.bar.2021.1080p.web.h264.dts-foobar"
    release_ac3 = "the.foo.bar.2021.1080p.web.h264.ac3-foobar"
    assert release_parser.score_subtitle_tokens(release_dts, release_ac3) == 100


def test_str_parser_edition_mismatch_collapses_score() -> None:
    extended = "the.foo.bar.2021.extended.1080p.web.h264-foobar"
    theatrical = "the.foo.bar.2021.1080p.web.h264-foobar"
    assert release_parser.score_subtitle_tokens(extended, theatrical) == 100
    extended_uncut = "the.foo.bar.2021.uncut.1080p.web.h264-foobar"
    assert release_parser.score_subtitle_tokens(extended, extended_uncut) <= 10


def test_str_parser_matching_edition_no_penalty() -> None:
    extended = "the.foo.bar.2021.extended.1080p.web.h264-foobar"
    assert release_parser.score_subtitle_tokens(extended, extended) == 100


def test_str_parser_proper_repack_not_edition_gate() -> None:
    proper = "the.foo.bar.2021.proper.1080p.web.h264-foobar"
    repack = "the.foo.bar.2021.repack.1080p.web.h264-foobar"
    assert release_parser.score_subtitle_tokens(proper, repack) == 100


def test_str_parser_new_source_tokens_leave_title() -> None:
    remux = release_parser._normalize_tokens("the.foo.bar.2021.1080p.remux-foobar")
    assert remux["source"] == "remux"
    assert "remux" not in remux["title"]


def test_str_parser_same_source_family_full_credit() -> None:
    web = "the.foo.bar.2021.1080p.web.h264-foobar"
    webdl = "the.foo.bar.2021.1080p.webdl.h264-foobar"
    assert release_parser.score_subtitle_tokens(web, webdl) == 100


def test_str_parser_compatible_source_families_partial_credit() -> None:
    web = "the.foo.bar.2021.1080p.web.h264-foobar"
    bluray = "the.foo.bar.2021.1080p.bluray.h264-foobar"
    hdtv = "the.foo.bar.2021.1080p.hdtv.h264-foobar"
    same = release_parser.score_subtitle_tokens(web, web)
    compatible = release_parser.score_subtitle_tokens(web, bluray)
    incompatible = release_parser.score_subtitle_tokens(web, hdtv)
    assert incompatible < compatible < same


def test_str_parser_dvd_broadcast_compatible() -> None:
    dvdrip = "the.foo.bar.2021.1080p.dvdrip.h264-foobar"
    hdtv = "the.foo.bar.2021.1080p.hdtv.h264-foobar"
    web = "the.foo.bar.2021.1080p.web.h264-foobar"
    compatible = release_parser.score_subtitle_tokens(dvdrip, hdtv)
    incompatible = release_parser.score_subtitle_tokens(dvdrip, web)
    assert incompatible < compatible


def test_str_parser_cam_never_syncs() -> None:
    cam = "the.foo.bar.2021.1080p.cam.h264-foobar"
    bluray = "the.foo.bar.2021.1080p.bluray.h264-foobar"
    web = "the.foo.bar.2021.1080p.web.h264-foobar"
    cam_vs_bluray = release_parser.score_subtitle_tokens(cam, bluray)
    same_source = release_parser.score_subtitle_tokens(web, web)
    assert release_parser._source_compatibility("cam", "cam") == 0.0
    assert cam_vs_bluray < same_source


def test_string_parser_movie() -> None:
    filename = "the.foo.bar.2021.1080p.web.h264-foobar"
    release_data = release_parser.get_release_info(filename)

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
    release_data = release_parser.get_release_info(filename)

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
    release_data = release_parser.get_release_info(filename)

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
    release_data = release_parser.get_release_info(filename)
    language_data = toml_file.load_toml_data(FILE_PATHS.subtitle_languages)
    create_provider_urls = release_parser.CreateProviderUrls(
        app_config,
        release_data,
        language_data,
    )
    provider_url = create_provider_urls.retrieve_urls()

    assert provider_url.opensubtitles == [
        "https://www.opensubtitles.org/en/search/sublanguageid-eng/searchonlymovies-on/moviename-the%20foo%20bar%20(2021)/rss_2_00"
    ]
    assert provider_url.opensubtitles_hash == ["https://www.opensubtitles.org/en/search/sublanguageid-eng/moviehash-"]
    assert provider_url.yifysubtitles == []


def test_provider_urls_series(monkeypatch) -> None:
    monkeypatch.setattr(release_parser, "VIDEO_FILE", fixture_data.FAKE_VIDEO_FILE_SERIES)
    app_config = toml_file.get_app_config(FILE_PATHS.config)
    filename = fixture_data.FAKE_VIDEO_FILE_SERIES.filename
    release_data = release_parser.get_release_info(filename)
    language_data = toml_file.load_toml_data(FILE_PATHS.subtitle_languages)
    create_provider_urls = release_parser.CreateProviderUrls(
        app_config,
        release_data,
        language_data,
    )
    provider_url = create_provider_urls.retrieve_urls()

    assert provider_url.opensubtitles == [
        "https://www.opensubtitles.org/en/search/sublanguageid-eng/searchonlytvseries-on/season-01/episode-01/moviename-the%20foo%20bar/rss_2_00"
    ]
    assert provider_url.opensubtitles_hash == ["https://www.opensubtitles.org/en/search/sublanguageid-eng/moviehash-"]
    assert provider_url.yifysubtitles == []
