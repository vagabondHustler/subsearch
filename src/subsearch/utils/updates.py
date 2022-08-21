import decimal
import re

import cloudscraper

from subsearch.data import __version__


def re_version(version: str, semantic: bool = False) -> str:
    try:
        rc = re.findall("[0-9]*\.[0-9]*\.[0-9]*-rc([0-9]*)", version)[0]
    except IndexError:
        rc = 0

    if semantic:
        # semantic expression https://regex101.com/r/2PNppl/1
        version_dots = ".".join(re.findall("(\d*\.\d*\.\d*-\w*\.\d*)|(\d*\.\d*\.\d*)", version)[0])
        return str(f"{version_dots}") if rc == 0 else str(f"{version_dots}-rc.{rc}")
    else:
        # float expression https://regex101.com/r/wt2fo6/1
        version_int = "".join(re.findall("(\d*)\.(\d*)\.(\d*)-\w*\.(\d*)|(\d*)\.(\d*)\.(\d*)", version)[0])
        return str(f"{version_int}.{rc}")


def scrape_github() -> str:
    """
    Scrape file  https://raw.githubusercontent.com/vagabondHustler/subsearch/main/src/subsearch/data/__version__.py

    Returns:
        str: returns the content of __version__.py
    """
    scraper = cloudscraper.create_scraper(browser={"browser": "chrome", "platform": "android", "desktop": False})
    url = "https://raw.githubusercontent.com/vagabondHustler/subsearch/main/src/subsearch/data/__version__.py"
    source = scraper.get(url)
    scontent = source.content
    file_content = str(scontent)
    return file_content


def get_current_version() -> str:
    return re_version(__version__)


def get_latest_version(semantic: bool = False) -> str:
    """
    Get the latest version number from subsearch github repo.
    As either a float or as semantic in str format

    Args:
        semantic (bool, optional): Decide which typ of string to return. Defaults to False.

    Returns:
        str:  xxx.x | x.x.x / x.x.x-rc.x
    """
    if semantic:
        version_github = scrape_github()
        return re_version(version_github, True)

    version_github = scrape_github()
    return re_version(version_github)


def is_new_version_avail() -> tuple[bool, bool]:
    """
    Check if there is a new version available over at github

    Returns:
        tuple[bool, bool]:
        stable release if True and False, release candidate if True and True
    """

    current_version = get_current_version()
    latest_version = get_latest_version()
    latest_rc = float(decimal.Decimal(latest_version) % 1)

    pre_release = False
    new_version = False
    if current_version < latest_version:
        if latest_rc > 0.0:
            pre_release = True
        else:
            pre_release = False
        new_version = True

    return new_version, pre_release


print(scrape_github())
