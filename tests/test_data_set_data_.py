import os

from src.subsearch.data import (
    __data__,
    __gui__,
    __home__,
    __icon__,
    __providers__,
    __tabs__,
    __titlebar__,
    __utils__,
)


def test_paths() -> None:
    assert __home__ == os.path.join(os.getcwd(), "src\\subsearch")
    assert __data__ == os.path.join(os.getcwd(), "src\\subsearch\\data")
    assert __gui__ == os.path.join(os.getcwd(), "src\\subsearch\\gui")
    assert __providers__ == os.path.join(os.getcwd(), "src\\subsearch\\providers")
    assert __utils__ == os.path.join(os.getcwd(), "src\\subsearch\\utils")
    assert __icon__ == os.path.join(os.getcwd(), "src\\subsearch\\gui\\assets\\icon\\subsearch.ico")
    assert __titlebar__ == os.path.join(os.getcwd(), "src\\subsearch\\gui\\assets\\titlebar")
    assert __tabs__ == os.path.join(os.getcwd(), "src\\subsearch\\gui\\assets\\tabs")
