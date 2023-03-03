import re

import cloudscraper
from packaging.version import Version

from subsearch.data import __version__


def find_semantic_version(version: str) -> str:
    """
    Parses a version string to extract the semantic version number.

    Args:
        version (str): The input version string. This could be any string containing a semantic version,
            but it is expected that there will be only one such version in the string.

    Returns:
        str: The extracted semantic version string.
    """
    # semantic expression https://regex101.com/r/M4qItH/2
    pattern = '"(\d*\.\d*\.\d*-\w*\d*)"|"(\d*\.\d*\.\d*-\w*\.\d*)"|"(\d*\.\d*\.\d*)"'
    version_semantic = "".join(re.findall(pattern, version)[0])
    return version_semantic


def scrape_github() -> str:
    """
    Scrape the latest version of the subsearch application from the subsearch GitHub repository.

    Args:
        None.

    Returns:
        str: Returns the file content which contains the latest version of the
             subsearch tool from the subsearch GitHub repository.
    """
    scraper = cloudscraper.create_scraper(browser={"browser": "chrome", "platform": "android", "desktop": False})
    url = "https://raw.githubusercontent.com/vagabondHustler/subsearch/main/src/subsearch/data/version.py"
    source = scraper.get(url)
    scontent = source.content
    file_content = str(scontent)
    return file_content


def get_latest_version() -> str:
    """
    Extracts the latest semantic version number from the GitHub repository.

    Returns:
        str: the latest version number in 'major.minor.patch-pre-release' format.
    """
    version_github = scrape_github()
    return find_semantic_version(version_github)


def is_new_version_avail() -> tuple[bool, bool]:
    """
    Checks for availability of new Subsearch version.

    Returns:
        tuple[bool, bool]: A tuple consisting of boolean values, new_is_avail and new_is_prerelease.
            If the new version is available, new_is_avail will be True, otherwise False.
            If the new version is a pre-release, new_is_prerelease will be True, otherwise False.
    """
    new_repo_avail, repo_is_prerelease = False, False
    released_version = get_latest_version()

    if Version(__version__) < Version(released_version):
        if Version(released_version).is_prerelease:
            repo_is_prerelease = True
        new_repo_avail = True

    return new_repo_avail, repo_is_prerelease
