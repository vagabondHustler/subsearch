import decimal
import re

import cloudscraper

from subsearch.data import __version__

SCRAPER = cloudscraper.create_scraper(browser={"browser": "chrome", "platform": "android", "desktop": False})


def re_version(_version: str, return_str: bool = False) -> str:
    try:
        rc = re.findall("[0-9]*\.[0-9]*\.[0-9]*-rc([0-9]*)", _version)[0]
    except IndexError:
        rc = 0

    if return_str:
        version = ".".join(re.findall("([0-9]*)\.([0-9]*)\.([0-9]*)", _version)[0])
        if rc == 0:
            return str(f"{version}")
        return str(f"{version}-rc{rc}")

    version = "".join(re.findall("([0-9]*)\.([0-9]*)\.([0-9]*)", _version)[0])
    return str(f"{version}.{rc}")


def scrape_github() -> str:
    source = SCRAPER.get(
        "https://raw.githubusercontent.com/vagabondHustler/subsearch/main/src/subsearch/data/__version__.py"
    )
    scontent = source.content
    _string = str(scontent)
    return _string


def latest_version_strfloat() -> str:
    version_github = scrape_github()
    return re_version(version_github)


def latest_version_str() -> str:
    version_github = scrape_github()
    return re_version(version_github, True)


def current_version_strfloat() -> str:
    return re_version(__version__)


def is_new_version_avail() -> tuple[bool, bool]:
    """
    Check if there is a new version available @ https://raw.githubusercontent.com/vagabondHustler/subsearch/main/src/subsearch/data/__version__.py

    Returns:
        tuple[bool, bool]:
        stable release if True and False, release candidate if True and True
    """

    current_version = current_version_strfloat()
    latest_version = latest_version_strfloat()

    latest_rc = float(decimal.Decimal(latest_version) % 1)

    # new version
    pre_release = False
    new_version = False
    if current_version < latest_version:
        if latest_rc > 0.0:
            pre_release = True
        else:
            pre_release = False
        new_version = True

    return new_version, pre_release
