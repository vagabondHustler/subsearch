import os
import sys
from pathlib import Path

NEW_VERSION = os.environ["NEW_VERSION"]
ID = os.environ["ID"]
VERSON_CONTROL_NAME = os.environ["VERSION_CONTROL_PATH"]
VERSION_PY_PATH = os.environ["VERSION_PY_PATH"]
MSI_NAME = os.environ["MSI_NAME"]
EXE_NAME = os.environ["EXE_NAME"]
HASHES_NAME = os.environ["HASHES_NAME"]
CHANGELOG_NAME = os.environ["CHANGELOG_NAME"]

STYLE_SEPERATOR = "-" * 120
VERSION_PATTERN = r"\d+\.\d+\.\d+(dev\d+)?"
FILE_PATHS = ["exe_installed", "exe_build", "msi_dist", "msi_artifact"]
TEST_NAMES = ["install", "executable", "uninstall"]
EXE_INSTALLED_PATH = Path.home() / "AppData" / "Local" / "Programs" / "Subsearch" / EXE_NAME
EXE_BUILD_PATH = Path.cwd() / "build" / f"exe.win-amd64-{sys.version_info[0]}.{sys.version_info[1]}" / EXE_NAME
MSI_DIST_PATH = Path.cwd() / "dist" / f"{MSI_NAME}"
MSI_ARTIFACT_PATH = Path("artifacts") / f"{MSI_NAME}"
HASHES_PATH = Path.cwd() / "artifacts" / HASHES_NAME
ARTIFACTS_PATH = Path.cwd() / "artifacts"
APP_LOG_PATH = Path.home() / "AppData" / "Local" / "Subsearch" / "log.log"
APP_CONFIG_PATH = Path.home() / "AppData" / "Local" / "Subsearch" / "config.toml"
VERSION_CONTROL_PATH = Path.cwd() / ".github" / "configs" / "version_control.json"
CHANGELOG_BUILDER_PATH = Path.cwd() / ".github" / "configs" / "changelog_builder.json"
VERSION_PYTON_PATH = Path(Path.cwd()) / "src" / "subsearch" / "data" / "version.py"
