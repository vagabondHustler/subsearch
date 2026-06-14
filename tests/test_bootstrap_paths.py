from pathlib import Path
from types import SimpleNamespace

import pytest

from subsearch.core.bootstrap import Bootstrap
from subsearch.runtime.config.constants import VIDEO_FILE


@pytest.fixture
def unanchored_video_file():
    saved = (
        VIDEO_FILE.file_exists,
        VIDEO_FILE.file_directory,
        VIDEO_FILE.file_path,
        VIDEO_FILE.extraction_directory,
        VIDEO_FILE.download_directory,
        VIDEO_FILE.filename,
        VIDEO_FILE.file_extension,
    )
    VIDEO_FILE.file_exists = False
    VIDEO_FILE.file_directory = Path("")
    VIDEO_FILE.filename = "movie"
    VIDEO_FILE.file_extension = ".mkv"
    yield
    (
        VIDEO_FILE.file_exists,
        VIDEO_FILE.file_directory,
        VIDEO_FILE.file_path,
        VIDEO_FILE.extraction_directory,
        VIDEO_FILE.download_directory,
        VIDEO_FILE.filename,
        VIDEO_FILE.file_extension,
    ) = saved


def _anchor_with_paths(download_directory: str, extraction_directory: str) -> None:
    paths = {"download_directory": download_directory, "extraction_directory": extraction_directory}
    fake_self = SimpleNamespace(app_config=SimpleNamespace(paths=paths))
    Bootstrap._anchor_working_directory(fake_self)  # type: ignore[arg-type]


def test_configured_directories_are_used_verbatim(unanchored_video_file, tmp_path) -> None:
    download = tmp_path / "downloads_here"
    extraction = tmp_path / "extract_here"
    _anchor_with_paths(str(download), str(extraction))

    assert VIDEO_FILE.file_directory == Path.home() / "Downloads"
    assert VIDEO_FILE.extraction_directory == extraction
    assert VIDEO_FILE.download_directory == download


def test_empty_directories_fall_back_to_temp_and_downloads(unanchored_video_file) -> None:
    from subsearch.runtime.config.constants import APP_PATHS

    _anchor_with_paths("", "")

    downloads = Path.home() / "Downloads"
    assert VIDEO_FILE.file_directory == downloads
    assert VIDEO_FILE.extraction_directory == downloads / "subs"
    assert VIDEO_FILE.download_directory == APP_PATHS.tmp_dir
