import re

import cloudscraper

from subsearch.data import __version__

SCRAPER = cloudscraper.create_scraper(browser={"browser": "chrome", "platform": "android", "desktop": False})


def check_for_updates() -> str:
    source = SCRAPER.get("https://raw.githubusercontent.com/vagabondHustler/SubSearch/main/src/subsearch/data/version.json")
    scontent = source.content
    _string = str(scontent)
    _string_no_qoute = _string.replace('"', " ")
    _string_items = _string_no_qoute.split(" ")
    for i in _string_items:
        if i.startswith("v") and i[-1].isnumeric():
            latest_version = i
            return latest_version


def is_new_version_available() -> tuple[bool, str] | tuple[bool, None]:
    """
    Compare local version with latest version on github

    Returns:
        tuple[bool, str]: True, None if local version is less than repo, False, "newer" if local version is greater than repo, False, else False None
    """

    local_version = re.findall(r"\d+", __version__)
    repo_version = re.findall(r"\d+", check_for_updates())

    if local_version < repo_version:
        return True, None
    if local_version > repo_version:
        return False, "newer"
    return False, None
