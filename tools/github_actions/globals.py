import sys
from pathlib import Path

STYLE_SEPARATOR = "-" * 120
TEST_NAMES = ["install", "executable", "uninstall"]

EXE_NAME = "Subsearch.exe"
HASHES_NAME = "hashes.sha256"
CHANGELOG_NAME = "changelog.md"

# Home paths created by the msi installer.
HOME_PATH = Path.home()
EXE_INSTALLED_PATH = HOME_PATH / "AppData" / "Local" / "Programs" / "Subsearch" / EXE_NAME
LOG_LOG_PATH = HOME_PATH / "AppData" / "Local" / "Subsearch" / "log.log"
CONFIG_TOML_PATH = HOME_PATH / "AppData" / "Local" / "Subsearch" / "config.toml"

# Build outputs in the working directory.
CWD_PATH = Path.cwd()
ARTIFACTS_PATH = CWD_PATH / "artifacts"
DIST_PATH = CWD_PATH / "dist"
EXE_FREEZE_PATH = CWD_PATH / "build" / f"exe.win-amd64-{sys.version_info[0]}.{sys.version_info[1]}" / EXE_NAME
HASHES_PATH = ARTIFACTS_PATH / HASHES_NAME


def msi_freeze_path() -> Path:
    """Return the single msi cx_Freeze built into ./dist.

    The file name embeds the version (Subsearch-<version>-win64.msi), so it is
    resolved by globbing at call time rather than from a name constant.
    """
    candidates = sorted(DIST_PATH.glob("*.msi"))
    if not candidates:
        raise FileNotFoundError(f"No .msi found in {DIST_PATH}")
    return candidates[0]
