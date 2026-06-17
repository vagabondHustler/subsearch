import tempfile
from pathlib import Path

from subsearch.runtime.config import paths


def test_app_paths() -> None:
    app_paths = paths.get_app_paths()
    assert app_paths.home.is_dir()
    assert app_paths.data.is_dir()
    assert app_paths.ui_assets.is_dir()
    assert app_paths.providers.is_dir()
    assert app_paths.io.is_dir()
    assert app_paths.tmp_dir == Path(tempfile.gettempdir()) / "tmp_subsearch"
