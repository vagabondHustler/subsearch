import re

import cloudscraper
from packaging.version import Version

from subsearch.data import __guid__, __version__


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

    if Version(__version__) < Version(released_version):
        if Version(released_version).is_prerelease:
            repo_is_prerelease = True
        new_repo_avail = True

    return new_repo_avail, repo_is_prerelease


# Work in progress
# def find_sha256(url):
#     response = requests.get(url)
#     html_content = response.text

#     parser = selectolax.parser.HTMLParser(html_content)
#     selector_lst = [
#         ".clearfix",
#         "div:nth-child(3)",
#         "section:nth-child(1)",
#         "div:nth-child(2)",
#         "div:nth-child(2)",
#         "div:nth-child(1)",
#         "div:nth-child(1)",
#         "div:nth-child(2)",
#         "h6:nth-child(5)",
#         "p:nth-child(2)",
#     ]

#     css_selector = " > ".join(selector_lst)

#     element = parser.css(css_selector)
#     match = re.search(r"([A-Fa-f0-9]{64})", element[0].html)
#     return match[0]
