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


def test_extract_skips_identical_content_already_in_destination(tmp_path) -> None:
    body = b"1\n00:00:00,000 --> 00:00:01,000\nfoo\n"
    destination = tmp_path / "subs"
    destination.mkdir()
    (destination / "movie.srt").write_bytes(body)
    with zipfile.ZipFile(tmp_path / "download.zip", "w") as archive:
        archive.writestr("movie.srt", body)

    extracted_count = file_system.extract_files_in_dir(tmp_path, destination)

    assert extracted_count == 0
    assert [path.name for path in destination.iterdir()] == ["movie.srt"]


def test_extract_versions_same_name_different_content(tmp_path) -> None:
    destination = tmp_path / "subs"
    destination.mkdir()
    (destination / "movie.srt").write_bytes(b"existing content\n")
    with zipfile.ZipFile(tmp_path / "download.zip", "w") as archive:
        archive.writestr("movie.srt", b"different content\n")

    extracted_count = file_system.extract_files_in_dir(tmp_path, destination)

    assert extracted_count == 1
    assert sorted(path.name for path in destination.iterdir()) == ["movie.srt", "movie_v1.srt"]


def test_extract_moves_loose_raw_subtitle_into_destination(tmp_path) -> None:
    download_directory = tmp_path / "tmp_subsearch"
    download_directory.mkdir()
    (download_directory / "movie.srt").write_bytes(b"raw subtitle\n")
    destination = tmp_path / "subs"
    destination.mkdir()

    extracted_count = file_system.extract_files_in_dir(download_directory, destination)

    assert extracted_count == 1
    assert [path.name for path in destination.iterdir()] == ["movie.srt"]
    assert not (download_directory / "movie.srt").exists()


def test_extract_skips_identical_loose_raw_subtitle(tmp_path) -> None:
    body = b"raw subtitle\n"
    download_directory = tmp_path / "tmp_subsearch"
    download_directory.mkdir()
    (download_directory / "movie.srt").write_bytes(body)
    destination = tmp_path / "subs"
    destination.mkdir()
    (destination / "movie.srt").write_bytes(body)

    extracted_count = file_system.extract_files_in_dir(download_directory, destination)

    assert extracted_count == 0
    assert [path.name for path in destination.iterdir()] == ["movie.srt"]


def _write_srt(directory: Path, name: str, body: bytes) -> Path:
    file_path = directory / name
    file_path.write_bytes(body)
    return file_path


def _zip_with(directory: Path, name: str, members: dict[str, bytes]) -> Path:
    archive_path = directory / name
    with zipfile.ZipFile(archive_path, "w") as archive:
        for member_name, body in members.items():
            archive.writestr(member_name, body)
    return archive_path


def test_extract_mixes_archives_and_raw_subtitles_in_one_pass(tmp_path) -> None:
    download_directory = tmp_path / "tmp_subsearch"
    download_directory.mkdir()
    destination = tmp_path / "subs"
    destination.mkdir()

    _zip_with(download_directory, "pack_one.zip", {"alpha.srt": b"alpha\n", "beta.ass": b"beta\n"})
    _zip_with(download_directory, "pack_two.zip", {"gamma.srt": b"gamma\n"})
    _write_srt(download_directory, "delta.srt", b"delta\n")
    _write_srt(download_directory, "epsilon.srt", b"epsilon\n")

    extracted_count = file_system.extract_files_in_dir(download_directory, destination)

    assert extracted_count == 5
    assert sorted(path.name for path in destination.iterdir()) == [
        "alpha.srt",
        "beta.ass",
        "delta.srt",
        "epsilon.srt",
        "gamma.srt",
    ]
    assert sorted(path.name for path in download_directory.iterdir()) == ["pack_one.zip", "pack_two.zip"]


def test_extract_dedups_raw_against_archive_with_same_name_and_sha(tmp_path) -> None:
    body = b"identical subtitle body\n"
    download_directory = tmp_path / "tmp_subsearch"
    download_directory.mkdir()
    destination = tmp_path / "subs"
    destination.mkdir()

    _zip_with(download_directory, "pack.zip", {"shared.srt": body})
    _write_srt(download_directory, "shared.srt", body)

    extracted_count = file_system.extract_files_in_dir(download_directory, destination)

    assert extracted_count == 1
    assert [path.name for path in destination.iterdir()] == ["shared.srt"]
    assert (destination / "shared.srt").read_bytes() == body


def test_extract_versions_raw_against_archive_with_same_name_different_sha(tmp_path) -> None:
    download_directory = tmp_path / "tmp_subsearch"
    download_directory.mkdir()
    destination = tmp_path / "subs"
    destination.mkdir()

    _zip_with(download_directory, "pack.zip", {"shared.srt": b"from archive\n"})
    _write_srt(download_directory, "shared.srt", b"from raw download\n")

    extracted_count = file_system.extract_files_in_dir(download_directory, destination)

    assert extracted_count == 2
    assert sorted(path.name for path in destination.iterdir()) == ["shared.srt", "shared_v1.srt"]


def test_extract_keeps_same_sha_differently_named_raw_subtitles(tmp_path) -> None:
    body = b"identical content across two names\n"
    download_directory = tmp_path / "tmp_subsearch"
    download_directory.mkdir()
    destination = tmp_path / "subs"
    destination.mkdir()

    _write_srt(download_directory, "ensure_same_sha_different_name_1.srt", body)
    _write_srt(download_directory, "ensure_same_sha_different_name_2.srt", body)

    extracted_count = file_system.extract_files_in_dir(download_directory, destination)

    assert extracted_count == 2
    assert sorted(path.name for path in destination.iterdir()) == [
        "ensure_same_sha_different_name_1.srt",
        "ensure_same_sha_different_name_2.srt",
    ]
    assert file_system.file_content_hash(
        destination / "ensure_same_sha_different_name_1.srt"
    ) == file_system.file_content_hash(destination / "ensure_same_sha_different_name_2.srt")


class _FakeResponse:
    def __init__(self, body: bytes, headers: dict[str, str]) -> None:
        self._body = body
        self.headers = headers
        self.status_code = 200

    def iter_content(self, chunk_size: int):
        for start in range(0, len(self._body), chunk_size):
            yield self._body[start : start + chunk_size]


class _FakeSession:
    def __init__(self, responses: dict[str, _FakeResponse]) -> None:
        self._responses = responses

    def get(self, url: str, headers=None, stream=False) -> _FakeResponse:
        return self._responses[url]


def _gestdown_subtitle(name: str, url: str) -> Subtitle:
    return Subtitle(
        token_result=100,
        provider_name="gestdown",
        subtitle_name=name,
        download_url=url,
        request_data={},
    )


def test_gestdown_raw_download_lands_in_tmp_then_moves_to_subs(tmp_path, monkeypatch) -> None:
    download_directory = tmp_path / "tmp_subsearch"
    download_directory.mkdir()
    destination = tmp_path / "subs"
    destination.mkdir()

    body = b"1\n00:00:00,000 --> 00:00:01,000\ngestdown\n"
    url = "https://api.gestdown.info/subtitles/download/abc"
    session = _FakeSession({url: _FakeResponse(body, {"content-type": "text/srt"})})
    monkeypatch.setattr("subsearch.io.http.get_session", lambda: session)

    subtitle = _gestdown_subtitle("the.show.s01e01.gestdown", url)
    downloaded = file_system.download_subtitle(subtitle, 1, 1, download_directory)

    assert downloaded is not None
    staged = list(download_directory.iterdir())
    assert [path.suffix for path in staged] == [".srt"]
    assert not list(destination.iterdir())

    extracted_count = file_system.extract_files_in_dir(download_directory, destination)

    assert extracted_count == 1
    assert [path.suffix for path in destination.iterdir()] == [".srt"]
    assert (next(destination.iterdir())).read_bytes() == body
    assert not list(download_directory.glob("*.srt"))


def test_download_subtitle_returns_stable_content_hash(tmp_path, monkeypatch) -> None:
    download_directory = tmp_path / "tmp_subsearch"
    download_directory.mkdir()

    body = b"1\n00:00:00,000 --> 00:00:01,000\nhash stability\n"
    url_one = "https://api.gestdown.info/subtitles/download/one"
    url_two = "https://api.gestdown.info/subtitles/download/two"
    different_url = "https://api.gestdown.info/subtitles/download/diff"
    session = _FakeSession(
        {
            url_one: _FakeResponse(body, {"content-type": "text/srt"}),
            url_two: _FakeResponse(body, {"content-type": "text/srt"}),
            different_url: _FakeResponse(b"different body\n", {"content-type": "text/srt"}),
        }
    )
    monkeypatch.setattr("subsearch.io.http.get_session", lambda: session)

    first = file_system.download_subtitle(_gestdown_subtitle("first", url_one), 1, 3, download_directory)
    second = file_system.download_subtitle(_gestdown_subtitle("second", url_two), 2, 3, download_directory)
    different = file_system.download_subtitle(_gestdown_subtitle("diff", different_url), 3, 3, download_directory)

    assert first is not None and second is not None and different is not None
    assert first.content_hash == second.content_hash
    assert first.content_hash != different.content_hash


def test_gestdown_raw_dedups_against_identical_archive_member(tmp_path, monkeypatch) -> None:
    download_directory = tmp_path / "tmp_subsearch"
    download_directory.mkdir()
    destination = tmp_path / "subs"
    destination.mkdir()

    shared_body = b"shared subtitle body\n"
    raw_url = "https://api.gestdown.info/subtitles/download/raw"
    zip_url = "https://opensubtitles.test/download/zip"
    zip_bytes_path = tmp_path / "source.zip"
    with zipfile.ZipFile(zip_bytes_path, "w") as archive:
        archive.writestr("shared.srt", shared_body)
        archive.writestr("extra.srt", b"only in archive\n")
    zip_bytes = zip_bytes_path.read_bytes()
    zip_bytes_path.unlink()

    session = _FakeSession(
        {
            raw_url: _FakeResponse(shared_body, {"content-type": "text/srt"}),
            zip_url: _FakeResponse(zip_bytes, {"content-type": "application/zip"}),
        }
    )
    monkeypatch.setattr("subsearch.io.http.get_session", lambda: session)

    raw_subtitle = _gestdown_subtitle("shared", raw_url)
    archive_subtitle = Subtitle(
        token_result=90,
        provider_name="opensubtitles",
        subtitle_name="opensub.pack",
        download_url=zip_url,
        request_data={},
    )

    assert file_system.download_subtitle(raw_subtitle, 1, 2, download_directory) is not None
    assert file_system.download_subtitle(archive_subtitle, 2, 2, download_directory) is not None

    extracted_count = file_system.extract_files_in_dir(download_directory, destination)

    # archive members extract first; the byte-identical raw "shared.srt" is sha-deduped, not versioned
    names = sorted(path.name for path in destination.iterdir())
    assert extracted_count == 2
    assert names == ["extra.srt", "shared.srt"]
    assert (destination / "shared.srt").read_bytes() == shared_body


def test_move_best_uses_video_name_and_preserves_existing_into_subs(tmp_path) -> None:
    video_directory = tmp_path / "video"
    subs_directory = tmp_path / "subs"
    video_directory.mkdir()
    subs_directory.mkdir()
    video_stem = "the.foo.bar.2021.1080p.web.h264-foobar"
    (video_directory / f"{video_stem}.srt").write_text("old subtitle\n", encoding="utf-8")
    source = _make_srt(subs_directory, "downloaded.srt")

    file_system.move_best_next_to_video(source, video_directory, video_stem, subs_directory)

    assert [path.name for path in video_directory.glob("*.srt")] == [f"{video_stem}.srt"]
    assert (video_directory / f"{video_stem}.srt").read_text(encoding="utf-8").startswith("1\n")
    assert (subs_directory / f"{video_stem}_tested.srt").read_text(encoding="utf-8") == "old subtitle\n"


def test_move_best_refuses_to_move_a_tested_subtitle(tmp_path) -> None:
    video_directory = tmp_path / "video"
    subs_directory = tmp_path / "subs"
    video_directory.mkdir()
    subs_directory.mkdir()
    video_stem = "the.foo.bar.2021.1080p.web.h264-foobar"
    tested_source = _make_srt(subs_directory, f"{video_stem}_tested_v1.srt")

    file_system.move_best_next_to_video(tested_source, video_directory, video_stem, subs_directory)

    assert list(video_directory.glob("*.srt")) == []
    assert tested_source.exists()


def test_tested_subtitles_are_excluded_from_candidates(tmp_path) -> None:
    video_stem = "the.foo.bar.2021.1080p.web.h264-foobar"
    _make_srt(tmp_path, f"{video_stem}.srt")
    _make_srt(tmp_path, f"{video_stem}_tested.srt")
    _make_srt(tmp_path, f"{video_stem}_tested_v1.srt")

    candidates = [path.name for path in file_system.subtitle_files_in(tmp_path)]

    assert candidates == [f"{video_stem}.srt"]


def _write_archive(directory: Path, name: str, member: str) -> Path:
    archive_path = directory / name
    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.writestr(member, "1\n00:00:00,000 --> 00:00:01,000\nfoo\n")
    return archive_path


def test_extract_files_in_dir_skips_excluded_ids(tmp_path) -> None:
    _write_archive(tmp_path, "auto12_random.zip", "auto.srt")
    _write_archive(tmp_path, "ui9999_random.zip", "ui.srt")
    destination = tmp_path / "subs"
    destination.mkdir()

    extracted_count = file_system.extract_files_in_dir(tmp_path, destination, exclude_ids={"ui9999"})

    assert extracted_count == 1
    assert [path.name for path in destination.iterdir()] == ["auto.srt"]


def test_count_extractable_archives_ignores_excluded_ids(tmp_path) -> None:
    _write_archive(tmp_path, "auto12_random.zip", "auto.srt")
    _write_archive(tmp_path, "ui9999_random.zip", "ui.srt")
    _make_subtitle(tmp_path, "loose.srt")

    assert file_system.count_extractable_archives(tmp_path, exclude_ids={"ui9999"}) == 2
    assert file_system.count_extractable_archives(tmp_path) == 3


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
