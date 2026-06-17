from pathlib import Path

from subsearch.io import file_system
from subsearch.runtime.config import SEARCH_SUBJECT, WORKSPACE

CWD = Path(Path.cwd()) / "tests" / "resources"
SUBS = Path(CWD) / "subs"


def test_search_subject_empty() -> None:
    assert SEARCH_SUBJECT.file_exists == False
    assert SEARCH_SUBJECT.search_term == ""
    assert SEARCH_SUBJECT.file_extension == ""
    assert SEARCH_SUBJECT.file_path is None


def test_workspace_empty() -> None:
    assert WORKSPACE.file_directory == Path(".")
    assert WORKSPACE.extraction_directory == Path(".")
    assert WORKSPACE.download_directory == Path(".")


def test_get_hash() -> None:
    hash0 = file_system.get_file_hash(CWD / "fake.test.movie.2022.1080p-group.mkv")
    hash1 = file_system.get_file_hash(CWD / "fake.none.hash.movie.mkv")
    assert hash0 == "43a17047da7e960e"
    assert hash1 == ""
