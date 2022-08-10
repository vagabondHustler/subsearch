import os

from src.subsearch.utils import local_paths


def test_local_paths_endswith() -> None:
    """
    test so to ensure that the local_paths.get_path function returns a with the correct extension or ends with the correct directory name
    """
    paths = ["data", "gui", "scraper", "utils", "icons", "buttons"]
    for p in paths:
        assert local_paths.get_path(p).endswith(p)
        assert local_paths.get_path(p, "file").endswith("file")


def test_local_paths_isdir() -> None:
    """
    test to ensure that the local_paths.get_path function finds the correct directory
    """
    paths = ["cwd", "root", "data", "gui", "scraper", "utils", "icons", "buttons"]
    for p in paths:
        assert os.path.isdir(local_paths.get_path(p))
