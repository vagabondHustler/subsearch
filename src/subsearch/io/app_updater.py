import subprocess
from pathlib import Path
from typing import Callable, NamedTuple

from curl_cffi.requests import exceptions

from subsearch.io import file_system
from subsearch.io.http import get_session
from subsearch.runtime.config import APP_PATHS
from subsearch.runtime.recorder import LogLevel, capture

REPOSITORY = "vagabondHustler/subsearch"
REPOSITORY_URL = f"https://github.com/{REPOSITORY}"
LATEST_RELEASE_PAGE = f"{REPOSITORY_URL}/releases/latest"
INSTALLER_DOWNLOAD = f"{REPOSITORY_URL}/releases/download"
INSTALLER_NAME = "Subsearch-{version}-win64.msi"


class ReleasePageError(Exception): ...


class ReleasePage(NamedTuple):
    final_url: str
    html: str


def fetch_latest_release_page() -> ReleasePage:
    try:
        response = get_session().get(LATEST_RELEASE_PAGE)
    except exceptions.RequestException as error:
        raise ReleasePageError(f"Could not reach GitHub: {error}") from error
    if not 200 <= response.status_code < 300:
        raise ReleasePageError(f"Could not fetch the latest version (HTTP {response.status_code})")
    return ReleasePage(final_url=response.url, html=response.text)


def installer_url(version: str) -> str:
    return f"{INSTALLER_DOWNLOAD}/{version}/{INSTALLER_NAME.format(version=version)}"


def download_installer(version: str, on_progress: Callable[[float], None] | None = None) -> Path:
    APP_PATHS.tmp_dir.mkdir(parents=True, exist_ok=True)
    destination = APP_PATHS.tmp_dir / INSTALLER_NAME.format(version=version)
    try:
        response = get_session().get(installer_url(version), stream=True)
    except exceptions.RequestException as error:
        capture("Update download failed", level=LogLevel.ERROR)
        raise ReleasePageError(f"Could not download version {version}: {error}") from error
    if not 200 <= response.status_code < 300:
        capture("Update download failed", level=LogLevel.ERROR)
        raise ReleasePageError(f"Could not download version {version} (HTTP {response.status_code})")
    file_system.download_response(destination, response, on_progress)
    capture(f"MSI file downloaded to: {destination}")
    return destination


def run_installer(msi_package_path: Path) -> None:
    subprocess.Popen(["msiexec.exe", "/i", str(msi_package_path)], creationflags=subprocess.DETACHED_PROCESS)
