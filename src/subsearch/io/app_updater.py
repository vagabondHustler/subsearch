import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import requests
from packaging.version import Version

from subsearch.runtime.logging.logger import log
from subsearch.runtime.config.constants import APP_PATHS, VERSION
from subsearch.io import file_system
from subsearch.io.http import get_session

REPOSITORY = "vagabondHustler/subsearch"
LATEST_VERSION_SOURCE = f"https://raw.githubusercontent.com/{REPOSITORY}/main/src/subsearch/runtime/version.py"
RELEASE_API = f"https://api.github.com/repos/{REPOSITORY}/releases/tags"
INSTALLER_DOWNLOAD = f"https://github.com/{REPOSITORY}/releases/download"


@dataclass(frozen=True, slots=True)
class UpdateAvailability:
    current_version: str
    latest_version: str
    update_available: bool
    is_prerelease: bool
    changelog: str


class VersionUnavailable(Exception): ...


def check_for_update() -> UpdateAvailability:
    latest_version = fetch_latest_version()
    update_available = Version(VERSION) < Version(latest_version)
    return UpdateAvailability(
        current_version=VERSION,
        latest_version=latest_version,
        update_available=update_available,
        is_prerelease=update_available and Version(latest_version).is_prerelease,
        changelog=fetch_release_changelog(latest_version),
    )


def fetch_latest_version() -> str:
    response = get_session().get(LATEST_VERSION_SOURCE)
    if response.status_code != 200:
        raise VersionUnavailable(f"Could not fetch the latest version (HTTP {response.status_code})")
    return parse_version(response.text)


def parse_version(version_source: str) -> str:
    # semantic expression https://regex101.com/r/M4qItH/
    pattern = r'(?<=__version__ = ")(\d+\.\d+\.\d+[a-zA-Z]*\d*).*?(?=")'
    matches = re.findall(pattern, version_source)
    if not matches:
        raise VersionUnavailable("Could not find a version in the latest release source")
    return "".join(matches[0])


def fetch_release_changelog(version: str) -> str:
    try:
        response = requests.get(f"{RELEASE_API}/{version}", headers={"Accept": "application/vnd.github+json"})
        if response.status_code != 200:
            return ""
        return response.json().get("body", "").strip()
    except requests.RequestException as error:
        log.error(str(error))
        return ""


def installer_url(version: str) -> str:
    return f"{INSTALLER_DOWNLOAD}/{version}/Subsearch-{version}-win64.msi"


def download_installer(version: str, on_progress: Callable[[float], None] | None = None) -> Path:
    APP_PATHS.tmp_dir.mkdir(parents=True, exist_ok=True)
    destination = APP_PATHS.tmp_dir / f"Subsearch-{version}-win64.msi"
    response = requests.get(installer_url(version), stream=True)
    if response.status_code != 200:
        log.error(f"Failed to download MSI file. HTTP Status Code: {response.status_code}")
        raise Exception(response.status_code)
    file_system.download_response(destination, response, on_progress)
    log.info(f"MSI file downloaded to: {destination}")
    return destination


def run_installer(msi_package_path: Path) -> None:
    command = f"msiexec.exe /i {msi_package_path}"
    subprocess.Popen(command, shell=True, creationflags=subprocess.DETACHED_PROCESS)


def download_and_update() -> None:
    log.event("banner", title="Updating Application")
    availability = check_for_update()
    if not availability.update_available:
        log.info("No new version available")
        return

    log.info("New version available")
    msi_package_path = download_installer(availability.latest_version)
    run_installer(msi_package_path)
    sys.exit()
