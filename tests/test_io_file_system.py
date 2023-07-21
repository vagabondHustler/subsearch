from pathlib import Path

from src.subsearch.data.constants import VIDEO_FILE
from src.subsearch.utils import io_file_system, io_winreg

CWD = Path(Path.cwd()) / "tests" / "resources"
SUBS = Path(CWD) / "subs"


def test_video_file_none() -> None:
    assert VIDEO_FILE is None


def test_get_hash() -> None:
    """
    test the get_hash function in src/subsearch/utils/io_file_system.py
    """
    hash0 = io_file_system.get_file_hash(CWD / "fake.test.movie.2022.1080p-group.mkv")
    hash1 = io_file_system.get_file_hash(CWD / "fake.none.hash.movie.mkv")
    assert hash0 == "43a17047da7e960e"
    assert hash1 == ""


def test_got_key() -> None:
    """
    test to ensure that the src/subsearch/utils/io_winreg.get_key function returns boolean
    """
    assert io_winreg.registry_key_exists() or io_winreg.registry_key_exists() is False
