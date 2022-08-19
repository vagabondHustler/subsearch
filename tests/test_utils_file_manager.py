import os
import shutil
from pathlib import Path

from src.subsearch.utils import file_manager


def copy_and_rename(src: str, dst: str):
    """copy and rename a file as __subsearch__<name>"""
    new_name = "__subsearch__" + Path(dst).name
    new_dst = Path(dst).with_name(new_name)
    shutil.copy2(src, new_dst)


CWD = os.path.join(os.getcwd(), "tests\\test_files")


def test_extract_zips() -> None:
    src = f"{CWD}\\test.subtitles.zip"
    dst = f"{CWD}\\test.subtitles.zip"
    copy_and_rename(src, dst)
    """
    test the extract_zips function in src/subsearch/utils/file_manager.py
    """
    file_manager.extract_zips(CWD, ".zip")


def test_rename_best_match() -> None:
    """
    test the rename_srts function in src/subsearch/utils/file_manager.py
    """
    file_manager.rename_best_match(f"test.movie.2022.1080p-group.srt", CWD, ".srt")


def test_clean_up() -> None:
    """
    test the clean_up function in file_manager.py
    """
    file_manager.clean_up(CWD, ".zip")
    file_manager.clean_up(CWD, ".srt")
    file_manager.clean_up(f"{CWD}\\subs", ".srt")


def test_get_hash() -> None:
    """
    test the get_hash function in src/subsearch/utils/file_manager.py
    """
    hash0 = file_manager.get_hash(f"{CWD}\\test.movie.2022.1080p-group.mkv")
    hash1 = file_manager.get_hash(f"{CWD}\\none.hash.movie.mkv")
    assert hash0 == "43a17047da7e960e"
    assert hash1 == None

