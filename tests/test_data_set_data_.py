import os

from src.subsearch.data import (
    __buttons__,
    __data__,
    __gui__,
    __icons__,
    __root__,
    __scraper__,
    __utils__,
    __video_directory__,
    __video_name__,
    __video_path__,
)


def test_paths() -> None:
    assert __root__ == os.path.join(os.getcwd(), "src\\subsearch")
    assert __data__ == os.path.join(os.getcwd(), "src\\subsearch\\data")
    assert __gui__ == os.path.join(os.getcwd(), "src\\subsearch\\gui")
    assert __scraper__ == os.path.join(os.getcwd(), "src\\subsearch\\scraper")
    assert __utils__ == os.path.join(os.getcwd(), "src\\subsearch\\utils")
    assert __icons__ == os.path.join(os.getcwd(), "src\\subsearch\\assets\\icons")
    assert __buttons__ == os.path.join(os.getcwd(), "src\\subsearch\\assets\\buttons")

