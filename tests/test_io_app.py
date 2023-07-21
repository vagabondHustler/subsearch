import tempfile
from pathlib import Path

from src.subsearch.data.constants import APP_PATHS


def test_paths() -> None:
    """Test function for APP_PATHS module.

    This function tests whether various path constants defined in APP_PATHS module are correctly defined.
    """
    assert APP_PATHS.home == Path(Path.cwd()) / "src" / "subsearch"
    assert APP_PATHS.data == Path(Path.cwd()) / "src" / "subsearch" / "data"
    assert APP_PATHS.gui == Path(Path.cwd()) / "src" / "subsearch" / "gui"
    assert APP_PATHS.gui_assets == Path(Path.cwd()) / "src" / "subsearch" / "gui" / "resources" / "assets"
    assert APP_PATHS.gui_styles == Path(Path.cwd()) / "src" / "subsearch" / "gui" / "resources" / "styles"
    assert APP_PATHS.providers == Path(Path.cwd()) / "src" / "subsearch" / "providers"
    assert APP_PATHS.utils == Path(Path.cwd()) / "src" / "subsearch" / "utils"
    assert APP_PATHS.tmp_dir == Path(tempfile.gettempdir()) / f"tmp_subsearch"
    assert APP_PATHS.app_data_local == Path.home() / "AppData" / "Local" / "Subsearch"
