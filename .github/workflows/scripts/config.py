import sys
from pathlib import Path

REPOSITORY_URL: str = "https://github.com/vagabondHustler/subsearch"
VIRUSTOTAL_FILE_URL: str = "https://www.virustotal.com/gui/file"

STYLE_SEPARATOR: str = "-" * 120

APP_NAME: str = "Subsearch"
EXE_NAME: str = f"{APP_NAME}.exe"
HASHES_NAME: str = "hashes.sha256"
CHANGELOG_NAME: str = "changelog.md"
# Must match subsearch.runtime.config.APP_USER_MODEL_ID so toasts inherit the shortcut's icon.
APP_USER_MODEL_ID: str = "Subsearch.Subsearch"


class Paths:
    home_directory: Path = Path.home()
    local_app_data: Path = home_directory / "AppData" / "Local"

    install_directory: Path = local_app_data / "Programs" / APP_NAME
    user_data_directory: Path = local_app_data / APP_NAME
    installed_executable: Path = install_directory / EXE_NAME
    log_file: Path = user_data_directory / "log.log"
    config_file: Path = user_data_directory / "config.json"
    start_menu_shortcut: Path = (
        home_directory / "AppData" / "Roaming" / "Microsoft" / "Windows" / "Start Menu" / "Programs" / f"{APP_NAME}.lnk"
    )

    working_directory: Path = Path.cwd()
    pyproject: Path = working_directory / "pyproject.toml"
    artifacts: Path = working_directory / "artifacts"
    dist: Path = working_directory / "dist"
    frozen_executable: Path = (
        working_directory / "build" / f"exe.win-amd64-{sys.version_info[0]}.{sys.version_info[1]}" / EXE_NAME
    )
    hashes: Path = artifacts / HASHES_NAME
    icon: Path = working_directory / "src" / "subsearch" / "ui" / "assets" / "subsearch.ico"
