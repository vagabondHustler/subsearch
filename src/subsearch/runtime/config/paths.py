import tempfile
from pathlib import Path

from subsearch.runtime.models import AppPaths, FilePaths

_APP_HOME = Path(__file__).resolve().parent.parent.parent


def get_app_paths() -> AppPaths:
    return AppPaths(
        home=_APP_HOME,
        data=_APP_HOME / "data",
        ui_assets=_APP_HOME / "ui" / "assets",
        providers=_APP_HOME / "providers",
        io=_APP_HOME / "io",
        parsing=_APP_HOME / "parsing",
        tmp_dir=Path(tempfile.gettempdir()) / "tmp_subsearch",
        appdata_subsearch=Path.home() / "AppData" / "Local" / "Subsearch",
    )


def get_file_paths() -> FilePaths:
    return FilePaths(
        log=Path.home() / "AppData" / "Local" / "Subsearch" / "log.log",
        config=Path.home() / "AppData" / "Local" / "Subsearch" / "config.json",
        subtitle_languages=_APP_HOME / "data" / "subtitle_languages.json",
    )
