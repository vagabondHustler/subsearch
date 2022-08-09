import cloudscraper

from . import version

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


def version_release(i: int) -> str:
    if i == 0:
        return "major"
    if i == 1:
        return "minor"
    if i == 2:
        return "patch"


def is_new_version_available() -> tuple:
    """
    Returns a tuple of (bool, str), where the bool is True if a new version is available, and the str is the type of release available.
    The str is either "major", "minor", "patch", "newer" or None.
    The bool is False if the current version is the latest version or your version is greater than the latest version on github.

    :return tuple: (bool, str)
    """
    _repo_version = check_for_updates()
    _local_version = version.current()
    repo_version = _repo_version.replace("v", "").split(".")
    local_version = _local_version.replace("v", "").split(".")

    for i, (rv, lv) in enumerate(zip(repo_version, local_version)):
        if int(rv) > int(lv):
            return True, version_release(i)
        if int(rv) < int(lv):
            return False, "newer"
    return False, None
