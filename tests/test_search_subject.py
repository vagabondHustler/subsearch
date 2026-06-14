from pathlib import Path

from subsearch.runtime.config.search_subject import SearchResolver
from subsearch.runtime.models import SearchSubject, Workspace

SUPPORTED_EXTENSIONS = ["mkv", "mp4", "avi"]


def _resolver() -> SearchResolver:
    return SearchResolver(SUPPORTED_EXTENSIONS)


def test_no_file_search_is_honest(tmp_path) -> None:
    subject, _ = _resolver().re_resolve("Terminator 2", tmp_path)

    assert subject.file_exists is False
    assert subject.search_term == "Terminator 2"
    assert subject.file_path is None
    assert subject.file_extension == ""


def test_real_file_derivation(tmp_path) -> None:
    video_file = tmp_path / "Movie.2021.mkv"
    video_file.touch()

    subject, workspace = _resolver().re_resolve("Movie.2021.mkv", tmp_path)

    assert subject.file_exists is True
    assert subject.search_term == "Movie.2021"
    assert subject.file_path == tmp_path / "Movie.2021.mkv"
    assert workspace.extraction_directory == tmp_path / "subs"
    assert workspace.download_directory == tmp_path / "tmp_subsearch"


def test_search_subject_copy_from_copies_only_subject_slots() -> None:
    target = SearchSubject(file_exists=False, search_term="", file_hash="", file_extension="", file_path=None)
    source = SearchSubject(
        file_exists=True,
        search_term="Movie.2021",
        file_hash="deadbeef",
        file_extension=".mkv",
        file_path=Path("/movies/Movie.2021.mkv"),
    )

    target.copy_from(source)

    assert target.file_exists is True
    assert target.search_term == "Movie.2021"
    assert target.file_hash == "deadbeef"
    assert target.file_extension == ".mkv"
    assert target.file_path == Path("/movies/Movie.2021.mkv")


def test_workspace_copy_from_copies_only_directories() -> None:
    target = Workspace(file_directory=Path(""), extraction_directory=Path(""), download_directory=Path(""))
    source = Workspace(
        file_directory=Path("/movies"),
        extraction_directory=Path("/movies/subs"),
        download_directory=Path("/movies/tmp_subsearch"),
    )

    target.copy_from(source)

    assert target.file_directory == Path("/movies")
    assert target.extraction_directory == Path("/movies/subs")
    assert target.download_directory == Path("/movies/tmp_subsearch")
