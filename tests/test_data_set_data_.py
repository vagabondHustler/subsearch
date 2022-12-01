from pathlib import Path

from src.subsearch.data import (
    __data__,
    __gui__,
    __home__,
    __icon__,
    __providers__,
    __tabs__,
    __utils__,
)


def test_paths() -> None:
    assert __home__ == Path(Path.cwd()) / "src" / "subsearch"
    assert __data__ == Path(Path.cwd()) / "src" / "subsearch" / "data"
    assert __gui__ == Path(Path.cwd()) / "src" / "subsearch" / "gui"
    assert __providers__ == Path(Path.cwd()) / "src" / "subsearch" / "providers"
    assert __utils__ == Path(Path.cwd()) / "src" / "subsearch" / "utils"
    assert __icon__ == Path(Path.cwd()) / "src" / "subsearch" / "gui" / "assets" / "icon" / "subsearch.ico"
    assert __tabs__ == Path(Path.cwd()) / "src" / "subsearch" / "gui" / "assets" / "tabs"
