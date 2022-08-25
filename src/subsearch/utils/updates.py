import re

import cloudscraper
from packaging.version import Version

from subsearch.data import __version__


def find_semantic_version(version: str) -> str:
    # semantic expression https://regex101.com/r/2PNppl/1
    version_semantic = "".join(re.findall("(\d*\.\d*\.\d*-\w*\.\d*)|(\d*\.\d*\.\d*)", version)[0])
    return version_semantic


def scrape_github() -> str:
    scraper = cloudscraper.create_scraper(browser={"browser": "chrome", "platform": "android", "desktop": False})
    url = "https://raw.githubusercontent.com/vagabondHustler/subsearch/main/src/subsearch/data/__version__.py"
    source = scraper.get(url)
    scontent = source.content
    file_content = str(scontent)
    return file_content


def get_latest_version() -> str:
    version_github = scrape_github()
    return find_semantic_version(version_github)


def is_new_version_avail() -> tuple[bool, bool]:
    """
    Check if the local version is up to date with the latest version in the github repository

    Returns:
        tuple[bool, bool]: new_is_avail, new_is_prerelease
    """
    new_repo_avail, repo_is_prerelease = False, False
    released_version = get_latest_version()

    if Version(__version__) < Version(released_version):
        if Version(released_version).is_prerelease:
            repo_is_prerelease = True
        new_repo_avail = True

    return new_repo_avail, repo_is_prerelease
