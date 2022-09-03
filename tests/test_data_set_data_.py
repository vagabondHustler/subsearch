import os

from src.subsearch.data import (
    __buttons__,
    __data__,
    __gui__,
    __home__,
    __icons__,
    __providers__,
    __tabs__,
    __utils__,
)


def test_paths() -> None:
    assert __home__ == os.path.join(os.getcwd(), "src\\subsearch")
    assert __data__ == os.path.join(os.getcwd(), "src\\subsearch\\data")
    assert __gui__ == os.path.join(os.getcwd(), "src\\subsearch\\gui")
    assert __providers__ == os.path.join(os.getcwd(), "src\\subsearch\\scraper")
    assert __utils__ == os.path.join(os.getcwd(), "src\\subsearch\\utils")
    assert __icons__ == os.path.join(os.getcwd(), "src\\subsearch\\assets\\icons")
    assert __buttons__ == os.path.join(os.getcwd(), "src\\subsearch\\assets\\buttons")
    assert __tabs__ == os.path.join(os.getcwd(), "src\\subsearch\\assets\\tabs")
