import zipfile
from pathlib import Path

from subsearch.io import file_system
from subsearch.runtime.models import MatchTier, Subtitle, classify_match_tier


def _make_srt(directory: Path, name: str) -> Path:
    return _make_subtitle(directory, name)


def _make_subtitle(directory: Path, name: str) -> Path:
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


def test_move_all_leaves_files_in_place_when_source_is_destination(tmp_path) -> None:
    _make_srt(tmp_path, "subtitle.srt")

    file_system.move_all(tmp_path, tmp_path)

    assert sorted(path.name for path in tmp_path.glob("*.srt")) == ["subtitle.srt"]


def test_move_all_moves_every_subtitle_extension_and_returns_count(tmp_path) -> None:
    source_directory = tmp_path / "subs"
    destination = tmp_path / "dst"
    source_directory.mkdir()
    destination.mkdir()
    for name in ("a.srt", "b.ass", "c.ssa", "d.sub", "e.vtt", "ignored.nfo"):
        _make_subtitle(source_directory, name)

    moved_count = file_system.move_all(source_directory, destination)

    assert moved_count == 5
    moved_names = sorted(path.name for path in destination.iterdir())
    assert moved_names == ["a.srt", "b.ass", "c.ssa", "d.sub", "e.vtt"]
    assert sorted(path.name for path in source_directory.iterdir()) == ["ignored.nfo"]


def test_count_subtitle_files_ignores_non_subtitles(tmp_path) -> None:
    _make_subtitle(tmp_path, "a.srt")
    _make_subtitle(tmp_path, "b.ass")
    _make_subtitle(tmp_path, "notes.nfo")

    assert file_system.count_subtitle_files(tmp_path) == 2


def test_extract_files_in_dir_returns_extracted_subtitle_count(tmp_path) -> None:
    archive_path = tmp_path / "download.zip"
    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.writestr("movie.srt", "1\n00:00:00,000 --> 00:00:01,000\nfoo\n")
        archive.writestr("movie.ass", "[Script Info]\n")
        archive.writestr("readme.nfo", "ignore me")
    destination = tmp_path / "subs"
    destination.mkdir()

    extracted_count = file_system.extract_files_in_dir(tmp_path, destination)

    assert extracted_count == 2
    assert sorted(path.name for path in destination.iterdir()) == ["movie.ass", "movie.srt"]


def test_extract_subtitle_by_id_unpacks_only_the_matching_archive(tmp_path) -> None:
    downloads = tmp_path / "downloads"
    downloads.mkdir()
    wanted_id = "aaaaa"
    other_id = "bbbbb"
    with zipfile.ZipFile(downloads / f"{wanted_id}.zip", "w") as archive:
        archive.writestr("wanted.srt", "1\n00:00:00,000 --> 00:00:01,000\nfoo\n")
    with zipfile.ZipFile(downloads / f"{other_id}.zip", "w") as archive:
        archive.writestr("other.srt", "1\n00:00:00,000 --> 00:00:01,000\nbar\n")
    destination = tmp_path / "subs"

    extracted_count = file_system.extract_subtitle_by_id(wanted_id, downloads, destination)

    assert extracted_count == 1
    assert [path.name for path in destination.iterdir()] == ["wanted.srt"]
