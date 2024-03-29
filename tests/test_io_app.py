import tempfile
from pathlib import Path

from subsearch.utils import io_app


def test_app_paths() -> None:
    app_paths = io_app.get_app_paths()
    assert app_paths.home.is_dir()
    assert app_paths.data.is_dir()
    assert app_paths.gui.is_dir()
    assert app_paths.gui_assets.is_dir()
    assert app_paths.gui_styles.is_dir()
    assert app_paths.providers.is_dir()
    assert app_paths.utils.is_dir()
    assert app_paths.tmp_dir == Path(tempfile.gettempdir()) / "tmp_subsearch"
