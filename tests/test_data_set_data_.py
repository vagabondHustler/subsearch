from pathlib import Path

from src.subsearch.data import __paths__


def test_paths() -> None:
    assert __paths__.home == Path(Path.cwd()) / "src" / "subsearch"
    assert __paths__.data == Path(Path.cwd()) / "src" / "subsearch" / "data"
    assert __paths__.gui == Path(Path.cwd()) / "src" / "subsearch" / "gui"
    assert __paths__.providers == Path(Path.cwd()) / "src" / "subsearch" / "providers"
    assert __paths__.utils == Path(Path.cwd()) / "src" / "subsearch" / "utils"
    assert __paths__.icon == Path(Path.cwd()) / "src" / "subsearch" / "gui" / "assets" / "icon" / "subsearch.ico"
    assert __paths__.tabs == Path(Path.cwd()) / "src" / "subsearch" / "gui" / "assets" / "tabs"
