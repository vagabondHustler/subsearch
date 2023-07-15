import tempfile
from pathlib import Path

from src.subsearch.data import app_paths


def test_paths() -> None:
    """Test function for app_paths module.

    This function tests whether various path constants defined in app_paths module are correctly defined.
    """
    assert app_paths.home == Path(Path.cwd()) / "src" / "subsearch"
    assert app_paths.data == Path(Path.cwd()) / "src" / "subsearch" / "data"
    assert app_paths.gui == Path(Path.cwd()) / "src" / "subsearch" / "gui"
    assert app_paths.gui_assets == Path(Path.cwd()) / "src" / "subsearch" / "gui" / "resources"/"assets"
    assert app_paths.gui_styles == Path(Path.cwd()) / "src" / "subsearch" / "gui" / "resources"/ "styles"
    assert app_paths.providers == Path(Path.cwd()) / "src" / "subsearch" / "providers"
    assert app_paths.utils == Path(Path.cwd()) / "src" / "subsearch" / "utils"
    assert app_paths.tmpdir == Path(tempfile.gettempdir()) / f"tmp_subsearch"
    assert app_paths.appdata_local == Path.home() / "AppData" / "Local" / "Subsearch"
