import time
from typing import NamedTuple

import cloudscraper
from bs4 import BeautifulSoup
from bs4.element import Tag

from subsearch.utils import log
from subsearch.utils.exceptions import CaptchaError
from subsearch.utils.raw_config import UserParameters
from subsearch.utils.string_parser import FileSearchParameters

SCRAPER = cloudscraper.create_scraper(browser={"browser": "chrome", "platform": "android", "desktop": False})


def get_lxml_doc(url: str, features: str = "lxml") -> BeautifulSoup:
    source = SCRAPER.get(url)
    scontent = source.content
    doc = BeautifulSoup(scontent, features)
    return doc


def log_and_sort_list(_provider: str, list_of_tuples: list[tuple[int, str, str]], pct: int):
    list_of_tuples.sort(key=lambda x: x[0], reverse=True)
    log.output(f"\n[Sorted List from {_provider}]", False)
    hbd_printed = False
    hnbd_printed = False
    for i in list_of_tuples:
        name = i[1]
        url = i[2]
        if i[0] >= pct and not hbd_printed:
            log.output(f"--- Has been downloaded ---\n", False)
            hbd_printed = True
        if i[0] <= pct and not hnbd_printed:
            log.output(f"--- Has not been downloaded ---\n", False)
            hnbd_printed = True
        log.output(f"{name}", False)
        log.output(f"{url}\n", False)
    return list_of_tuples


class DownloadData(NamedTuple):
    name: str
    file_path: str
    url: str
    idx_num: int
    idx_lenght: int


class BaseProvider:
    """
    Base class for providers
    """

    def __init__(self, parameters: FileSearchParameters, user_parameters: UserParameters):
        # file parameters
        self.url_subscene = parameters.url_subscene
        self.url_opensubtitles = parameters.url_opensubtitles
        self.url_hash = parameters.url_opensubtitles_hash
        self.title = parameters.title
        self.year = parameters.year
        self.season = parameters.season
        self.season_ordinal = parameters.season_ordinal
        self.episode = parameters.episode
        self.episode_ordinal = parameters.episode_ordinal
        self.series = parameters.series
        self.release = parameters.release
        self.group = parameters.group
        self.file_hash = parameters.file_hash
        self.definitive_match = parameters.definitive_match
        # user parameters
        self.current_language = user_parameters.current_language
        self.hearing_impaired = user_parameters.hearing_impaired
        self.pct = user_parameters.pct
        self.show_download_window = user_parameters.show_dl_window
        # sorted_list
        self._sorted_list: list[DownloadData] = []


class BaseChecks:
    """
    Base class for checks
    """

    def __init__(self) -> None:
        pass

    def is_movie(self, key: str, title: str, year: int) -> bool:
        if key.lower() == f"{title} ({year})":
            log.output(f"Movie {key} found")
            return True
        return False

    def try_the_year_before(self, key: str, title: str, year: int) -> bool:
        # Some releases are released close to the next year. If so, the year might differ from the year in the title.
        # This function subtracts one year from the year in the title and checks if the release is in the list.
        if year == "N/A":
            return False
        _year = int(year) - 1
        the_year_before = f"{title} ({_year})"
        if key.lower().startswith(the_year_before):
            log.output(f"Movie {key} found")
            return True
        return False

    def is_series(self, key: str, title: str, season_ordinal: str, show_bool: bool) -> bool:
        if title and season_ordinal in key.lower() and show_bool:
            log.output(f"TV-Series {key} found")
            return True
        return False

    def is_threshold_met(
        self, key: str, title: str, season: str, episode: str, show_bool: bool, number: int, pct: int
    ) -> bool:
        if number >= pct or title and f"{season}{episode}" in key.lower() and show_bool:
            return True
        return False

    def is_subtitle_hearing_impaired(self, a1: Tag) -> bool | None:
        a1_parent = a1.parent
        class_a40 = a1_parent.find("td", class_="a40")  # non-hearing impaired
        class_a41 = a1_parent.find("td", class_="a41")  # hearing imparted
        if class_a40 is None:
            return True
        elif class_a41 is None:
            return False
        return None

    def to_many_requests(body: Tag):
        time.sleep(1)
        log.output(f"ToManyRequestsWarning: To many requests, sleept for 1 second")

    def is_captcha(self, doc: Tag):
        tag_h2 = doc.find("h2", text="Why do I have to complete a CAPTCHA?")
        if tag_h2 is not None:
            raise CaptchaError("Captcha protection detected. Please try again later.")
