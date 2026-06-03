import sys
from pathlib import Path

REPOSITORY_URL = "https://github.com/vagabondHustler/subsearch"
VIRUSTOTAL_FILE_URL = "https://www.virustotal.com/gui/file"

STYLE_SEPARATOR = "-" * 120

EXE_NAME = "Subsearch.exe"
HASHES_NAME = "hashes.sha256"
CHANGELOG_NAME = "changelog.md"

HOME_PATH = Path.home()
EXE_INSTALLED_PATH = HOME_PATH / "AppData" / "Local" / "Programs" / "Subsearch" / EXE_NAME
LOG_LOG_PATH = HOME_PATH / "AppData" / "Local" / "Subsearch" / "log.log"
CONFIG_TOML_PATH = HOME_PATH / "AppData" / "Local" / "Subsearch" / "config.toml"

CWD_PATH = Path.cwd()
ARTIFACTS_PATH = CWD_PATH / "artifacts"
DIST_PATH = CWD_PATH / "dist"
EXE_FREEZE_PATH = CWD_PATH / "build" / f"exe.win-amd64-{sys.version_info[0]}.{sys.version_info[1]}" / EXE_NAME
HASHES_PATH = ARTIFACTS_PATH / HASHES_NAME


def msi_name(version: str) -> str:
    return f"Subsearch-{version}-win64.msi"


def artifact_id(version: str, ref_name: str, run_id: str) -> str:
    return f"{version}_{ref_name}_{run_id}"


def build_artifact_name(artifact_id: str) -> str:
    return f"build_{artifact_id}"


def changelog_artifact_name(artifact_id: str) -> str:
    return f"changelog_{artifact_id}"


def msi_freeze_path() -> Path:
    candidates = sorted(DIST_PATH.glob("*.msi"))
    if not candidates:
        raise FileNotFoundError(f"No .msi found in {DIST_PATH}")
    return candidates[0]
