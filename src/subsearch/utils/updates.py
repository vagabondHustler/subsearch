import decimal
import re

import cloudscraper

from subsearch.data import __version__


def re_version(version: str, semantic: bool = False) -> str:
    try:
        pre_num = re.findall(f"\d*\.\d*\.\d*-\w*\.(\d*)", version)[0]
    except IndexError:
        pre_num = 0

    if semantic:
        # semantic expression https://regex101.com/r/2PNppl/1
        version_semantic = "".join(re.findall("(\d*\.\d*\.\d*-\w*\.\d*)|(\d*\.\d*\.\d*)", version)[0])
        return str(f"{version_semantic}")
    else:
        # float expression https://regex101.com/r/wt2fo6/1
        version_num = "".join(re.findall("(\d*)\.(\d*)\.(\d*)-\w*\.(\d*)|(\d*)\.(\d*)\.(\d*)", version)[0])
        return str(f"{version_num}.{pre_num}")


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


def get_current_version(semantic: bool = False) -> str:
    if semantic:
        return __version__
    return re_version(__version__)


def get_latest_version(semantic: bool = False) -> str:
    """
    Get the latest version number from subsearch github repo.
    As either a float or as semantic in str format

    Args:
        semantic (bool, optional): Decide which typ of string to return. Defaults to False.

    Returns:
        str:  xxx.x | x.x.x / x.x.x-type.x
    """
    if semantic:
        version_github = scrape_github()
        return re_version(version_github, True)

    version_github = scrape_github()
    return re_version(version_github)


def define_pre_release_worth(cver: str, csemantic: str, lver: str, lsemantic: str) -> tuple[float, float]:
    """
    Add int to float if rc, beta or alpha is found in semantic version

    rc = 3, beta = 2, alpha = 1

    x.x.x-beta.1 would equal float(2.1)

    Args:
        cver (str): current version as xxx.x
        csemantic (str): current version as semantic
        lver (str): latest version as xxx.x
        lsemantic (str): latest version as semantic

    Returns:
        tuple[float, float]:
    """
    # cver and lver needs to be a str otherwise it would return as 0.10.....something and not 0.1
    current_float = float(decimal.Decimal(cver) % 1)
    latest_float = float(decimal.Decimal(lver) % 1)
    semantic_versions = [csemantic, lsemantic]
    for num, item in enumerate(semantic_versions):
        if "-rc" in item:
            if num == 0:
                current_float += 3
            if num == 1:
                latest_float += 3
        elif "-beta" in item:
            if num == 0:
                current_float += 2
            if num == 1:
                latest_float += 2
        elif "-alpha" in item:
            if num == 0:
                current_float += 1
            if num == 1:
                latest_float += 1

    return current_float, latest_float


def is_new_version_avail() -> tuple[bool, bool]:
    """
    Check if there is a new version available over at the subsearch repo

    Returns:
        tuple[bool, bool]:
        stable release if True and False, pre-release if True and True
    """
    new_version = False
    pre_release = False

    curr_ver, curr_semantic = get_current_version(), get_current_version(semantic=True)
    ltst_ver, ltst_semantic = get_latest_version(), get_latest_version(semantic=True)
    curr_float, ltst_float = define_pre_release_worth(curr_ver, curr_semantic, ltst_ver, ltst_semantic)

    if curr_ver < ltst_ver:
        if curr_float < ltst_float:
            pre_release = True
        else:
            pre_release = False
        new_version = True

    return new_version, pre_release
