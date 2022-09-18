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


class DownloadData(NamedTuple):
    name: str
    file_path: str
    url: str
    idx_num: int
    idx_lenght: int


class FormattedData(NamedTuple):
    provider: str
    release: str
    url: str
    pct_result: int
    formatted_release: str
    formatted_url: str


class BaseProvider:
    """
    Base class for providers
    """

    def __init__(self, parameters: FileSearchParameters, user_parameters: UserParameters):
        # file parameters
        self.parameters = parameters
        self.user_parameters = user_parameters
        self.url_subscene = parameters.url_subscene
        self.url_opensubtitles = parameters.url_opensubtitles
        self.url_opensubtitles_hash = parameters.url_opensubtitles_hash
        self.url_yifysubtitles = parameters.url_yifysubtitles
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
        self.hi_sub = user_parameters.hearing_impaired
        self.non_hi_sub = user_parameters.non_hearing_impaired
        self.pct_threashold = user_parameters.percentage
        self.show_download_window = user_parameters.show_download_window

    def is_movie(self, key: str) -> bool:
        if key.lower() == f"{self.title} ({self.year})":
            log.output(f"Movie {key} found")
            return True
        return False

    def try_the_year_before(self, key: str) -> bool:
        # Some releases are released close to the next year. If so, the year might differ from the year in the title.
        # This function subtracts one year from the year in the title and checks if the release is in the list.
        if self.year == 0000:
            return False
        _year = int(self.year) - 1
        the_year_before = f"{self.title} ({_year})"
        if key.lower().startswith(the_year_before):
            log.output(f"Movie {key} found")
            return True
        return False

    def is_series(self, key: str) -> bool:
        if self.title and self.season_ordinal in key.lower() and self.series:
            log.output(f"TV-Series {key} found")
            return True
        return False

    def is_threshold_met(self, key: str, pct_result: int) -> bool:
        if pct_result >= self.pct_threashold or self.title and f"{self.season}{self.episode}" in key.lower() and self.series:
            return True
        return False

    def is_subtitle_hearing_impaired(self, a1: Tag) -> bool | None:
        a1_parent = a1.parent
        regular_subtitle = a1_parent.find("td", class_="a40")  # regular
        hearing_impaired_subtitle = a1_parent.find("td", class_="a41")  # hearing impaired
        if regular_subtitle is not None:
            return False
        elif hearing_impaired_subtitle is not None:
            return True
        return None

    def to_many_requests(self):
        time.sleep(1)
        log.output(f"ToManyRequestsWarning: To many requests, sleept for 1 second")

    def is_captcha(self, doc: Tag):
        tag_h2 = doc.find("h2", text="Why do I have to complete a CAPTCHA?")
        if tag_h2 is not None:
            raise CaptchaError("Captcha protection detected. Please try again later.")


def get_lxml_doc(url: str, features: str = "lxml") -> BeautifulSoup:
    source = SCRAPER.get(url)
    scontent = source.content
    doc = BeautifulSoup(scontent, features)
    return doc


def named_tuple_zip_data(provider: str, video_tmp_directory: str, to_be_downloaded: dict[str, str]) -> list[DownloadData]:
    download_info = []
    tbd_lenght = len(to_be_downloaded)
    for zip_idx, (zip_name, zip_url) in enumerate(to_be_downloaded.items(), start=1):
        zip_fp = f"{video_tmp_directory}\\{provider}_{zip_idx}.zip"
        data = DownloadData(name=zip_name, file_path=zip_fp, url=zip_url, idx_num=zip_idx, idx_lenght=tbd_lenght)
        download_info.append(data)
    return download_info


def format_key_value_pct(_provider: str, key: str, value: str, _pct_result: int) -> FormattedData:
    lenght_str = sum(1 for char in f"[{_pct_result:>3}%  match]:")
    number_of_spaces = " " * lenght_str
    _match_release = f"[{_pct_result:>3}%  match]: {key}"
    _url = f"{number_of_spaces} {value}"
    data = FormattedData(
        provider=_provider,
        release=key,
        url=value,
        pct_result=_pct_result,
        formatted_release=_match_release,
        formatted_url=_url,
    )
    return data


def log_and_sort_list(_provider: str, _list: list[FormattedData], pct: int) -> list[FormattedData]:
    _list.sort(key=lambda x: x.pct_result, reverse=True)
    log.output(f"\n[Sorted List from {_provider}]", False)
    hbd_printed = False
    hnbd_printed = False
    for data in _list:
        if data.pct_result >= pct and not hbd_printed:
            log.output(f"--- Has been downloaded ---\n", False)
            hbd_printed = True
        if data.pct_result <= pct and not hnbd_printed:
            log.output(f"--- Has not been downloaded ---\n", False)
            hnbd_printed = True
        log.output(f"{data.formatted_release}", False)
        log.output(f"{data.formatted_url}\n", False)
    return _list
