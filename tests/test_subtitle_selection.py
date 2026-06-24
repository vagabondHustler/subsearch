from pathlib import Path

from subsearch.io import file_system
from subsearch.parsing import subtitle_selection


def _make_subtitle(directory: Path, name: str) -> Path:
    file_path = directory / name
    file_path.write_text("1\n00:00:00,000 --> 00:00:01,000\nfoo\n", encoding="utf-8")
    return file_path


def test_find_best_subtitle_match_prefers_hash_over_equal_token_score(tmp_path) -> None:
    release = "the.foo.bar.2021.1080p.web.h264-foobar"
    _make_subtitle(tmp_path, f"{release}.srt")
    _make_subtitle(tmp_path, f"{file_system._HASH_MATCH_PREFIX}{release}.srt")

    best = subtitle_selection.find_best_subtitle_match(release, tmp_path)

    assert best.name.startswith(file_system._HASH_MATCH_PREFIX)


def test_find_best_subtitle_match_picks_highest_token_score(tmp_path) -> None:
    release = "the.foo.bar.2021.1080p.web.h264-foobar"
    _make_subtitle(tmp_path, "completely.unrelated.movie.1999.dvdrip-xyz.srt")
    _make_subtitle(tmp_path, f"{release}.srt")

    best = subtitle_selection.find_best_subtitle_match(release, tmp_path)

    assert best.name == f"{release}.srt"


def test_find_best_subtitle_match_breaks_ties_on_first_file(tmp_path) -> None:
    release = "the.foo.bar.2021.1080p.web.h264-foobar"
    _make_subtitle(tmp_path, f"a.{release}.srt")
    _make_subtitle(tmp_path, f"b.{release}.srt")

    best = subtitle_selection.find_best_subtitle_match(release, tmp_path)

    assert best.name == f"a.{release}.srt"


def test_find_best_subtitle_match_considers_non_srt_extensions(tmp_path) -> None:
    release = "the.foo.bar.2021.1080p.web.h264-foobar"
    _make_subtitle(tmp_path, "completely.unrelated.movie.1999.dvdrip-xyz.srt")
    _make_subtitle(tmp_path, f"{release}.ass")

    best = subtitle_selection.find_best_subtitle_match(release, tmp_path)

    assert best.name == f"{release}.ass"


def test_autoload_rename_keeps_matched_extension(tmp_path) -> None:
    release = "the.foo.bar.2021.1080p.web.h264-foobar"
    _make_subtitle(tmp_path, f"downloaded.{release}.ass")

    renamed = subtitle_selection.autoload_rename(release, tmp_path)

    assert renamed.name == f"{release}.ass"
    assert renamed.exists()
