from pathlib import Path

from subsearch.runtime.config.constants import VIDEO_FILE
from subsearch.io import file_system, windows_registry

CWD = Path(Path.cwd()) / "tests" / "resources"
SUBS = Path(CWD) / "subs"


def test_video_file_False() -> None:
    assert VIDEO_FILE.file_exists == False
    assert VIDEO_FILE.filename == ""
    assert VIDEO_FILE.file_extension == ""
    assert VIDEO_FILE.file_path == Path(".")
    assert VIDEO_FILE.file_directory == Path(".")
    assert VIDEO_FILE.subs_dir == Path(".")
    assert VIDEO_FILE.tmp_dir == Path(".")


def test_get_hash() -> None:
    hash0 = file_system.get_file_hash(CWD / "fake.test.movie.2022.1080p-group.mkv")
    hash1 = file_system.get_file_hash(CWD / "fake.none.hash.movie.mkv")
    assert hash0 == "43a17047da7e960e"
    assert hash1 == ""
