import shutil
from pathlib import Path

from src.subsearch.utils import file_manager, local_paths


def copy_and_rename(src: str, dst: str):
    """copy and rename a file as __subsearch__<name>"""
    new_name = "__subsearch__" + Path(dst).name
    new_dst = Path(dst).with_name(new_name)
    shutil.copy2(src, new_dst)


SRC = f'{local_paths.get_path("cwd")}\\tests\\test_files\\test.subtitles.zip'
DST = f'{local_paths.get_path("cwd")}\\tests\\test_files\\test.subtitles.zip'
CWD = f'{local_paths.get_path("cwd")}\\tests\\test_files'
copy_and_rename(SRC, DST)


# extract all zip file in said directory
def test_extract_zips() -> None:
    """
    test the extract_zips function in file_manager.py
    """
    file_manager.extract_zips(CWD, ".zip")


# rename a .srts to the same as video release name
def test_rename_srts() -> None:
    """
    test the rename_srts function in file_manager.py
    """
    file_manager.rename_srts(f"test.movie.2022.1080p-group.srt", CWD, f"group.srt", ".srt")


# move unused .srt to /subs/
def test_move_files() -> None:
    """
    test the move_files function in file_manager.py
    """
    file_manager.move_files(CWD, "group.srt", ".srt")


# remove .zips
def test_clean_up() -> None:
    """
    test the clean_up function in file_manager.py
    """
    file_manager.clean_up(CWD, ".zip")
    file_manager.clean_up(CWD, ".srt")
    file_manager.clean_up(f"{CWD}\\subs", ".srt")


# get file hash
def test_get_hash() -> None:
    """
    test the get_hash function in file_manager.py
    """
    hash0 = file_manager.get_hash(f"{CWD}\\test.movie.2022.1080p-group.mkv")
    hash1 = file_manager.get_hash(f"{CWD}\\none.hash.movie.mkv")
    assert hash0 == "43a17047da7e960e"
    assert hash1 == None
