import sys
from pathlib import Path

from tools.cli.handlers.io_python import read_string

STYLE_SEPERATOR = "-" * 120
APP_VERISON = read_string()
EXE_INSTALLED = Path.home() / "AppData" / "Local" / "Programs" / "Subsearch" / "Subsearch.exe"
EXE_BUILD = Path.cwd() / "build" / f"exe.win-amd64-{sys.version_info[0]}.{sys.version_info[1]}" / "Subsearch.exe"
MSI_DIST = Path.cwd() / "dist" / f"Subsearch-{APP_VERISON}-win64.msi"
MSI_ARTIFACT = Path("artifacts") / f"Subsearch-{APP_VERISON}-win64.msi"
HASHES_PATH = Path.cwd() / "artifacts" / "hashes.sha256"
ARTIFACTS_PATH = Path.cwd() / "artifacts"
PRE_RELEASE = ["rc", "a", "b", "alpha", "beta", "dev"]
APP_LOG_PATH = Path.home() / "AppData" / "Local" / "Subsearch" / "log.log"
APP_CONFIG_PATH = Path.home() / "AppData" / "Local" / "Subsearch" / "config.toml"
VERSION_CONTROL_PATH = Path.cwd() / ".github" / "configs" / "version_control.json"
CHANGELOG_BUILDER = Path.cwd() / ".github" / "configs" / "changelog_builder.json"
PACKAGEPATH = Path(__file__).resolve().parent.as_posix()
