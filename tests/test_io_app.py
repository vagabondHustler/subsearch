import tempfile
from pathlib import Path

from src.subsearch.utils import io_app





def test_paths() -> None:
    """Test function for APP_PATHS module.

    This function tests whether various path constants defined in APP_PATHS module are correctly defined.
    """
    app_paths = io_app.get_app_paths()
    assert app_paths.home == Path.cwd() / "src" / "subsearch"
    assert app_paths.data == Path.cwd() / "src" / "subsearch" / "data"
    assert app_paths.gui == Path.cwd() / "src" / "subsearch" / "gui"
    assert app_paths.gui_assets == Path.cwd() / "src" / "subsearch" / "gui" / "resources" / "assets"
    assert app_paths.gui_styles == Path.cwd() / "src" / "subsearch" / "gui" / "resources" / "styles"
    assert app_paths.providers == Path.cwd() / "src" / "subsearch" / "providers"
    assert app_paths.utils == Path.cwd() / "src" / "subsearch" / "utils"
    assert app_paths.tmp_dir == Path(tempfile.gettempdir()) / f"tmp_subsearch"
    assert app_paths.app_data_local == Path.home() / "AppData" / "Local" / "Subsearch"
