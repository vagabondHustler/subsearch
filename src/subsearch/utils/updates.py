import re
from typing import Optional

import cloudscraper

from subsearch.data import __version__

SCRAPER = cloudscraper.create_scraper(browser={"browser": "chrome", "platform": "android", "desktop": False})


def check_for_updates() -> str:
    source = SCRAPER.get(
        "https://raw.githubusercontent.com/vagabondHustler/subsearch/main/src/subsearch/data/__version__.py"
    )
    scontent = source.content
    _string = str(scontent)
    latest_version = "".join(re.findall('^.*["]([0-9]*)\.([0-9]*)\.([0-9]*)["]', _string)[0])
    return latest_version


def is_new_version_available() -> tuple[bool, Optional[str]]:
    """
    Compare local version with latest version on github

    Returns:
        tuple[bool, str]: True, None if local version is less than repo, False, "newer" if local version is greater than repo, False, else False None
    """

    local_version = "".join(re.findall("([0-9]*)\.([0-9]*)\.([0-9]*)", __version__)[0])
    repo_version = check_for_updates()
    if local_version < repo_version:
        return True, None
    if local_version > repo_version:
        return False, "newer"
    return False, None
