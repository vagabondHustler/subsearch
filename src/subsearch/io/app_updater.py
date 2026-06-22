import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Callable
from urllib.parse import unquote, urlparse

from curl_cffi.requests import exceptions
from packaging.version import InvalidVersion, Version
from selectolax.lexbor import LexborHTMLParser

from subsearch.io import file_system
from subsearch.io.http import get_session
from subsearch.runtime.config import APP_PATHS, VERSION
from subsearch.runtime.logging.events import LogEvent
from subsearch.runtime.logging.logger import log

REPOSITORY = "vagabondHustler/subsearch"
REPOSITORY_URL = f"https://github.com/{REPOSITORY}"
LATEST_RELEASE_PAGE = f"{REPOSITORY_URL}/releases/latest"
INSTALLER_DOWNLOAD = f"{REPOSITORY_URL}/releases/download"
INSTALLER_NAME = "Subsearch-{version}-win64.msi"

_RELEASE_TAG_PATTERN = re.compile(r"/releases/tag/([^/?#]+)$")


@dataclass(frozen=True, slots=True)
class GitHubRelease:
    version: str
    changelog: str


@dataclass(frozen=True, slots=True)
class UpdateAvailability:
    current_version: str
    latest_version: str
    update_available: bool
    is_prerelease: bool
    changelog: str


class VersionUnavailable(Exception): ...


def check_for_update() -> UpdateAvailability:
    latest_release = fetch_latest_release()
    update_available = Version(VERSION) < Version(latest_release.version)
    return UpdateAvailability(
        current_version=VERSION,
        latest_version=latest_release.version,
        update_available=update_available,
        is_prerelease=update_available and Version(latest_release.version).is_prerelease,
        changelog=latest_release.changelog,
    )


def fetch_latest_release() -> GitHubRelease:
    try:
        response = get_session().get(LATEST_RELEASE_PAGE)
    except exceptions.RequestException as error:
        raise VersionUnavailable(f"Could not reach GitHub: {error}") from error
    if not 200 <= response.status_code < 300:
        raise VersionUnavailable(f"Could not fetch the latest version (HTTP {response.status_code})")
    return GitHubRelease(version=parse_release_version(response.url), changelog=parse_release_changelog(response.text))


def parse_release_version(release_url: str) -> str:
    release_path = urlparse(release_url).path
    match = _RELEASE_TAG_PATTERN.search(release_path)
    if match is None:
        raise VersionUnavailable("Could not find a release tag on GitHub")
    version = unquote(match.group(1))
    try:
        Version(version)
    except InvalidVersion as error:
        raise VersionUnavailable(f"GitHub returned an invalid release version: {version}") from error
    return version


def parse_release_changelog(release_page: str) -> str:
    changelog = LexborHTMLParser(release_page).css_first(".markdown-body")
    return changelog.text(separator="\n", strip=True) if changelog is not None else ""


def installer_url(version: str) -> str:
    return f"{INSTALLER_DOWNLOAD}/{version}/{INSTALLER_NAME.format(version=version)}"


def download_installer(version: str, on_progress: Callable[[float], None] | None = None) -> Path:
    APP_PATHS.tmp_dir.mkdir(parents=True, exist_ok=True)
    destination = APP_PATHS.tmp_dir / INSTALLER_NAME.format(version=version)
    try:
        response = get_session().get(installer_url(version), stream=True)
    except exceptions.RequestException as error:
        log.event(LogEvent.UPDATE_FAILED, level="error")
        raise VersionUnavailable(f"Could not download version {version}: {error}") from error
    if not 200 <= response.status_code < 300:
        log.event(LogEvent.UPDATE_FAILED, level="error", status_code=response.status_code)
        raise VersionUnavailable(f"Could not download version {version} (HTTP {response.status_code})")
    file_system.download_response(destination, response, on_progress)
    log.event(LogEvent.UPDATE_DOWNLOADED, destination=destination)
    return destination


def run_installer(msi_package_path: Path) -> None:
    subprocess.Popen(["msiexec.exe", "/i", str(msi_package_path)], creationflags=subprocess.DETACHED_PROCESS)
