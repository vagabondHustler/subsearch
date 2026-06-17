import os
import sys
from pathlib import Path
from tools.github_actions import install_module


def environs_exists():
    try:
        os.environ["NEW_VERSION"]
    except KeyError:
        return False
    return True


if not environs_exists():
    dotenv = install_module._dotenv()
    dotenv.load_dotenv(".env")  # type: ignore

NEW_VERSION = os.environ["NEW_VERSION"]
ID = os.environ["ID"]
VERSION_CONTROL_PATH = os.environ["VERSION_CONTROL_PATH"]
VERSION_PY_PATH = os.environ["VERSION_PY_PATH"]
MSI_NAME = os.environ["MSI_NAME"]
EXE_NAME = os.environ["EXE_NAME"]
HASHES_NAME = os.environ["HASHES_NAME"]
CHANGELOG_NAME = os.environ["CHANGELOG_NAME"]


STYLE_SEPERATOR = "-" * 120
VERSION_PATTERN = r"\d+\.\d+\.\d+(dev\d+)?"
FILE_PATHS = ["exe_installed", "exe_build", "msi_dist", "msi_artifact"]
TEST_NAMES = ["install", "executable", "uninstall"]

# home paths (created by msi installer)
HOME_PATH = Path.home()
EXE_INSTALLED_PATH = HOME_PATH / "AppData" / "Local" / "Programs" / "Subsearch" / EXE_NAME
LOG_LOG_PATH = HOME_PATH / "AppData" / "Local" / "Subsearch" / "log.log"
CONFIG_TOML_PATH = HOME_PATH / "AppData" / "Local" / "Subsearch" / "config.toml"

# current working directory paths
CWD_PATH = Path.cwd()
ARTIFACTS_PATH = CWD_PATH / "artifacts"
EXE_FREEZE_PATH = CWD_PATH / "build" / f"exe.win-amd64-{sys.version_info[0]}.{sys.version_info[1]}" / EXE_NAME
MSI_FREEZE_PATH = CWD_PATH / "dist" / MSI_NAME
CHANGELOG_BUILDER_JSON_PATH = CWD_PATH / ".github" / "configs" / "changelog_builder.json"

# artifacts
MSI_ARTIFACT_PATH = ARTIFACTS_PATH / MSI_NAME
HASHES_PATH = ARTIFACTS_PATH / HASHES_NAME
