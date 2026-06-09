from pathlib import Path
from types import SimpleNamespace

from subsearch.io import file_system
from subsearch.runtime.models.model import MatchTier, Subtitle, classify_match_tier


def _make_srt(directory: Path, name: str) -> Path:
    file_path = directory / name
    file_path.write_text("1\n00:00:00,000 --> 00:00:01,000\nfoo\n", encoding="utf-8")
    return file_path


def test_subtitle_hash_match_defaults_false() -> None:
    subtitle = Subtitle(
        token_result=100,
        provider_name="opensubtitles",
        subtitle_name="the.foo.bar.2021.1080p.web.h264-foobar",
        download_url="https://example.test/sub",
        request_data={},
    )
    assert subtitle.hash_match is False
    assert (
        Subtitle(
            token_result=100,
            provider_name="opensubtitles",
            subtitle_name="x",
            download_url="x",
            request_data={},
            hash_match=True,
        ).hash_match
        is True
    )


def test_classify_match_tier_ladder() -> None:
    assert classify_match_tier(hash_match=True, percentage_result=0, accept_threshold=90) is MatchTier.S
    assert classify_match_tier(hash_match=False, percentage_result=100, accept_threshold=90) is MatchTier.A
    assert classify_match_tier(hash_match=False, percentage_result=90, accept_threshold=90) is MatchTier.B
    assert classify_match_tier(hash_match=False, percentage_result=89, accept_threshold=90) is MatchTier.C
    assert MatchTier.S > MatchTier.A > MatchTier.B > MatchTier.C


def test_find_best_subtitle_match_prefers_hash_over_equal_token_score(monkeypatch, tmp_path) -> None:
    release = "the.foo.bar.2021.1080p.web.h264-foobar"
    _make_srt(tmp_path, f"{release}.srt")
    _make_srt(tmp_path, f"{file_system._HASH_MATCH_PREFIX}{release}.srt")
    monkeypatch.setattr(file_system, "VIDEO_FILE", SimpleNamespace(subs_dir=tmp_path))

    best = file_system.find_best_subtitle_match(release)

    assert best.name.startswith(file_system._HASH_MATCH_PREFIX)


def test_find_best_subtitle_match_picks_highest_token_score(monkeypatch, tmp_path) -> None:
    release = "the.foo.bar.2021.1080p.web.h264-foobar"
    _make_srt(tmp_path, "completely.unrelated.movie.1999.dvdrip-xyz.srt")
    _make_srt(tmp_path, f"{release}.srt")
    monkeypatch.setattr(file_system, "VIDEO_FILE", SimpleNamespace(subs_dir=tmp_path))

    best = file_system.find_best_subtitle_match(release)

    assert best.name == f"{release}.srt"


def test_find_best_subtitle_match_breaks_ties_on_first_file(monkeypatch, tmp_path) -> None:
    release = "the.foo.bar.2021.1080p.web.h264-foobar"
    _make_srt(tmp_path, f"a.{release}.srt")
    _make_srt(tmp_path, f"b.{release}.srt")
    monkeypatch.setattr(file_system, "VIDEO_FILE", SimpleNamespace(subs_dir=tmp_path))

    best = file_system.find_best_subtitle_match(release)

    assert best.name == f"a.{release}.srt"


def test_rename_subtitle_to_release_versions_on_collision(tmp_path) -> None:
    release = "the.foo.bar.2021.1080p.web.h264-foobar"
    _make_srt(tmp_path, f"{release}.srt")
    source = _make_srt(tmp_path, "downloaded.srt")

    renamed = file_system.rename_subtitle_to_release(source, release)

    assert renamed.name == f"{release}_v1.srt"


def test_move_all_versions_colliding_files(tmp_path) -> None:
    source_directory = tmp_path / "subs"
    destination = tmp_path / "dst"
    source_directory.mkdir()
    destination.mkdir()
    _make_srt(destination, "subtitle.srt")
    _make_srt(source_directory, "subtitle.srt")

    file_system.move_all(source_directory, destination)

    moved_names = sorted(path.name for path in destination.glob("*.srt"))
    assert moved_names == ["subtitle.srt", "subtitle_v1.srt"]
