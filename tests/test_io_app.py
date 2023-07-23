import tempfile
from pathlib import Path

from subsearch.utils import io_app


def test_app_paths() -> None:
    """Test function for APP_PATHS module.

    This function tests whether various path constants defined in APP_PATHS module are correctly defined.
    """
    app_paths = io_app.get_app_paths()
    assert app_paths.home.is_dir()
    assert app_paths.data.is_dir()
    assert app_paths.gui.is_dir()
    assert app_paths.gui_assets.is_dir()
    assert app_paths.gui_styles.is_dir()
    assert app_paths.providers.is_dir()
    assert app_paths.utils.is_dir()
    assert app_paths.tmp_dir == Path(tempfile.gettempdir()) / "tmp_subsearch"
    assert app_paths.tmp_dir.is_dir()