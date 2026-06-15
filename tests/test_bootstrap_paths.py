from pathlib import Path
from types import SimpleNamespace

import pytest

from subsearch.core.bootstrap import Bootstrap
from subsearch.runtime.config import SEARCH_SUBJECT, WORKSPACE


@pytest.fixture
def unanchored_search():
    saved_subject = (
        SEARCH_SUBJECT.file_exists,
        SEARCH_SUBJECT.file_path,
        SEARCH_SUBJECT.search_term,
        SEARCH_SUBJECT.file_extension,
    )
    saved_workspace = (
        WORKSPACE.file_directory,
        WORKSPACE.extraction_directory,
        WORKSPACE.download_directory,
    )
    SEARCH_SUBJECT.file_exists = False
    SEARCH_SUBJECT.file_path = None
    SEARCH_SUBJECT.search_term = "movie"
    SEARCH_SUBJECT.file_extension = ".mkv"
    WORKSPACE.file_directory = Path("")
    yield
    (
        SEARCH_SUBJECT.file_exists,
        SEARCH_SUBJECT.file_path,
        SEARCH_SUBJECT.search_term,
        SEARCH_SUBJECT.file_extension,
    ) = saved_subject
    (
        WORKSPACE.file_directory,
        WORKSPACE.extraction_directory,
        WORKSPACE.download_directory,
    ) = saved_workspace


def _anchor_with_paths(download_directory: str, extraction_directory: str) -> None:
    paths = {"download_directory": download_directory, "extraction_directory": extraction_directory}
    fake_self = SimpleNamespace(app_config=SimpleNamespace(paths=paths))
    Bootstrap._anchor_working_directory(fake_self)  # type: ignore[arg-type]


def test_configured_directories_are_used_verbatim(unanchored_search, tmp_path) -> None:
    download = tmp_path / "downloads_here"
    extraction = tmp_path / "extract_here"
    _anchor_with_paths(str(download), str(extraction))

    assert WORKSPACE.file_directory == Path.home() / "Downloads"
    assert WORKSPACE.extraction_directory == extraction
    assert WORKSPACE.download_directory == download


def test_empty_directories_fall_back_to_temp_and_downloads(unanchored_search) -> None:
    from subsearch.runtime.config import APP_PATHS

    _anchor_with_paths("", "")

    downloads = Path.home() / "Downloads"
    assert WORKSPACE.file_directory == downloads
    assert WORKSPACE.extraction_directory == downloads / "subs"
    assert WORKSPACE.download_directory == APP_PATHS.tmp_dir


def test_anchor_overwrites_workspace_only(unanchored_search) -> None:
    _anchor_with_paths("", "")

    assert SEARCH_SUBJECT.file_exists is False
    assert SEARCH_SUBJECT.search_term == "movie"
    assert SEARCH_SUBJECT.file_path is None
