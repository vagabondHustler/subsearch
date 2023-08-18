from pathlib import Path

from subsearch.data.constants import VIDEO_FILE
from subsearch.utils import io_file_system, io_winreg

CWD = Path(Path.cwd()) / "tests" / "resources"
SUBS = Path(CWD) / "subs"


def test_video_file_none() -> None:
    assert VIDEO_FILE is None


def test_get_hash() -> None:
    hash0 = io_file_system.get_file_hash(CWD / "fake.test.movie.2022.1080p-group.mkv")
    hash1 = io_file_system.get_file_hash(CWD / "fake.none.hash.movie.mkv")
    assert hash0 == "43a17047da7e960e"
    assert hash1 == ""


def test_got_key() -> None:
    assert io_winreg.registry_key_exists() or io_winreg.registry_key_exists() is False
