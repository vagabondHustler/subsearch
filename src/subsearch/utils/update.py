import re
import subprocess
import sys
from pathlib import Path

import cloudscraper
import requests
from packaging.version import Version

from subsearch.globals import log
from subsearch.globals.constants import APP_PATHS, VERSION
from subsearch.utils import io_file_system


def find_semantic_version(version: str) -> str:
    # semantic expression https://regex101.com/r/M4qItH/
    pattern = r'(?<=__version__ = ")(\d+\.\d+\.\d+[a-zA-Z]*\d*).*?(?=")'
    version_semantic = "".join(re.findall(pattern, version)[0])
    return version_semantic


def scrape_github() -> str:
    scraper = cloudscraper.create_scraper(browser={"browser": "chrome", "platform": "android", "desktop": False})
    url = "https://raw.githubusercontent.com/vagabondHustler/subsearch/main/src/subsearch/data/version.py"
    source = scraper.get(url)
    scontent = source.content
    file_content = str(scontent)
    return file_content


def get_latest_version() -> str:
    version_github = scrape_github()
    return find_semantic_version(version_github)


def is_new_version_avail() -> tuple[bool, bool]:
    new_repo_avail, repo_is_prerelease = False, False
    released_version = get_latest_version()

    if Version(VERSION) < Version(released_version):
        if Version(released_version).is_prerelease:
            repo_is_prerelease = True
        new_repo_avail = True

    return new_repo_avail, repo_is_prerelease


def get_latest_msi_url(latest_version: str = "") -> str:
    return f"https://github.com/vagabondHustler/subsearch/releases/download/{latest_version}/Subsearch-{latest_version}-win64.msi"


def run_installer(msi_package_path: Path) -> None:
    command = f"msiexec.exe /i {msi_package_path}"
    subprocess.Popen(command, shell=True, creationflags=subprocess.DETACHED_PROCESS)


def download_and_update():
    log.brackets("Updating Application")
    latest_version = get_latest_version()
    latest_msi = get_latest_msi_url(latest_version)
    if Version(VERSION) > Version(latest_version):
        log.stdout(f"No new version available")
        return None

    log.stdout(f"New version available")
    if not APP_PATHS.tmp_dir.exists():
        APP_PATHS.tmp_dir.mkdir(parents=True, exist_ok=True)
    msi_package_path = APP_PATHS.tmp_dir / f"Subsearch-{latest_version}-win64.msi"
    response = requests.get(latest_msi, stream=True)
    if response.status_code == 200:
        io_file_system.download_response(msi_package_path, response)
        msg = f"MSI file downloaded to: {msi_package_path}"
        log.stdout(f"MSI file downloaded to: {msi_package_path}")
    else:
        msg = f"Failed to download MSI file. HTTP Status Code: {response.status_code}"
        log.stdout(msg, level="error")
        raise Exception(response.status_code)
    run_installer(msi_package_path)
    sys.exit()
