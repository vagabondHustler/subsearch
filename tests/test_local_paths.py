import os

from src.subsearch.utils import local_paths


def test_local_paths_endswith() -> None:
    paths = ["data", "gui", "scraper", "utils", "icons", "buttons"]
    for p in paths:
        assert local_paths.get_path(p).endswith(p)
        assert local_paths.get_path(p, "file").endswith("file")


def test_local_paths_isdir() -> None:
    paths = ["cwd", "root", "data", "gui", "scraper", "utils", "icons", "buttons"]
    for p in paths:
        assert os.path.isdir(local_paths.get_path(p))
