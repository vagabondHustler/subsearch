import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import requests
from packaging.version import Version

from subsearch.runtime.logger import log
from subsearch.runtime.constants import APP_PATHS, VERSION
from subsearch.io import file_system
from subsearch.io.http import get_session


@dataclass(frozen=True, slots=True)
class UpdateAvailability:
    current_version: str
    latest_version: str
    update_available: bool
    is_prerelease: bool
    changelog: str


class VersionUnavailable(Exception): ...


def find_semantic_version(version: str) -> str:
    # semantic expression https://regex101.com/r/M4qItH/
    pattern = r'(?<=__version__ = ")(\d+\.\d+\.\d+[a-zA-Z]*\d*).*?(?=")'
    matches = re.findall(pattern, version)
    if not matches:
        raise VersionUnavailable("Could not find a version in the latest release source")
    return "".join(matches[0])


def scrape_github() -> str:
    session = get_session()
    url = "https://raw.githubusercontent.com/vagabondHustler/subsearch/main/src/subsearch/runtime/version.py"
    source = session.get(url)
    if source.status_code != 200:
        raise VersionUnavailable(f"Could not fetch the latest version (HTTP {source.status_code})")
    return source.text


def get_latest_version() -> str:
    version_github = scrape_github()
    return find_semantic_version(version_github)


def get_release_changelog(latest_version: str) -> str:
    url = f"https://api.github.com/repos/vagabondHustler/subsearch/releases/tags/{latest_version}"
    try:
        response = requests.get(url, headers={"Accept": "application/vnd.github+json"})
        if response.status_code != 200:
            return ""
        return response.json().get("body", "").strip()
    except requests.RequestException as error:
        log.stdout(str(error), level="error")
        return ""


def check_for_update() -> UpdateAvailability:
    latest_version = get_latest_version()
    update_available = Version(VERSION) < Version(latest_version)
    is_prerelease = update_available and Version(latest_version).is_prerelease
    return UpdateAvailability(
        current_version=VERSION,
        latest_version=latest_version,
        update_available=update_available,
        is_prerelease=is_prerelease,
        changelog=get_release_changelog(latest_version),
    )


def is_new_version_avail() -> tuple[bool, bool]:
    availability = check_for_update()
    return availability.update_available, availability.is_prerelease


def get_latest_msi_url(latest_version: str = "") -> str:
    return f"https://github.com/vagabondHustler/subsearch/releases/download/{latest_version}/Subsearch-{latest_version}-win64.msi"


def run_installer(msi_package_path: Path) -> None:
    command = f"msiexec.exe /i {msi_package_path}"
    subprocess.Popen(command, shell=True, creationflags=subprocess.DETACHED_PROCESS)


def download_installer(
    latest_version: str, on_progress: Callable[[float], None] | None = None
) -> Path:
    if not APP_PATHS.tmp_dir.exists():
        APP_PATHS.tmp_dir.mkdir(parents=True, exist_ok=True)
    msi_package_path = APP_PATHS.tmp_dir / f"Subsearch-{latest_version}-win64.msi"
    response = requests.get(get_latest_msi_url(latest_version), stream=True)
    if response.status_code != 200:
        log.stdout(
            f"Failed to download MSI file. HTTP Status Code: {response.status_code}", level="error"
        )
        raise Exception(response.status_code)
    file_system.download_response(msi_package_path, response, on_progress)
    log.stdout(f"MSI file downloaded to: {msi_package_path}")
    return msi_package_path


def download_and_update() -> None:
    log.brackets("Updating Application")
    availability = check_for_update()
    if not availability.update_available:
        log.stdout("No new version available")
        return None

    log.stdout("New version available")
    msi_package_path = download_installer(availability.latest_version)
    run_installer(msi_package_path)
    sys.exit()
