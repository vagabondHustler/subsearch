import time
from typing import NamedTuple

import cloudscraper
from bs4 import BeautifulSoup
from bs4.element import Tag

from subsearch.data import __video_directory__
from subsearch.utils import log, string_parser
from subsearch.utils.exceptions import CaptchaError
from subsearch.utils.raw_config import UserParameters
from subsearch.utils.string_parser import FileSearchParameters

SCRAPER = cloudscraper.create_scraper(browser={"browser": "chrome", "platform": "android", "desktop": False})


def get_lxml_doc(url: str) -> BeautifulSoup:
    source = SCRAPER.get(url)
    scontent = source.content
    doc = BeautifulSoup(scontent, "lxml")
    return doc


def log_and_sort_list(list_of_tuples: list[tuple[int, str, str]], pct: int):
    list_of_tuples.sort(key=lambda x: x[0], reverse=True)
    log.output("\n[Sorted List from Subscene]")
    hbd_printed = False
    hnbd_printed = False
    for i in list_of_tuples:
        name = i[1]
        url = i[2]
        if i[0] >= pct and not hbd_printed:
            log.output(f"--- Has been downloaded ---\n")
            hbd_printed = True
        if i[0] <= pct and not hnbd_printed:
            log.output(f"--- Has not been downloaded ---\n")
            hnbd_printed = True
        log.output(f"{name}\n{url}\n")
    return list_of_tuples


class SubsceneData(NamedTuple):
    file_path: str
    url: str
    idx_num: int
    idx_lenght: int


class Subscene:
    def __init__(self, parameters: FileSearchParameters, user_parameters: UserParameters):
        # file parameters
        self.url_subscene = parameters.url_subscene
        self.title = parameters.title
        self.year = parameters.year
        self.season = parameters.season
        self.season_ordinal = parameters.season_ordinal
        self.episode = parameters.episode
        self.episode_ordinal = parameters.episode_ordinal
        self.show_bool = parameters.show_bool
        self.release = parameters.release
        self.group = parameters
        # user parameters
        self.language = user_parameters.language
        self.lang_code2 = user_parameters.lang_code2
        self.hearing_impaired = user_parameters.hearing_impaired
        self.pct = user_parameters.pct
        self.show_download_window = user_parameters.show_dl_window
        # scraper
        self.scrape = SubsceneScrape()
        # checks
        self.check = SubsceneChecks()

    def parse(self):
        to_be_scraped: list[str] = []
        title_keys = self.scrape.title(self.url_subscene)
        for key, value in title_keys.items():
            if self.check.is_movie(key, self.title, self.year):
                to_be_scraped.append(value) if value not in (to_be_scraped) else None
            if self.check.try_the_year_before(key, self.title, self.year):
                to_be_scraped.append(value) if value not in (to_be_scraped) else None
            if self.check.is_show_bool(key, self.title, self.season_ordinal, self.show_bool, self.lang_code2):
                to_be_scraped.append(value) if value not in (to_be_scraped) else None
        log.output("Done with task\n") if len(to_be_scraped) > 0 else None

        # exit if no titles found
        if len(to_be_scraped) == 0:
            if self.show_bool:
                log.output("")
                log.output(f"No TV-series found matching {self.title}")
            else:
                log.output("")
                log.output(f"No movies found matching {self.title}")
            return None

        # search title for subtitles
        to_be_downloaded: list[str] = []
        to_be_sorted: list[tuple[int, str, str]] = []
        while len(to_be_scraped) > 0:
            for subtitle_url in to_be_scraped:
                log.output(f"[Searching for subtitles]")
                sub_keys = self.scrape.subtitle(self.language, self.hearing_impaired, subtitle_url)
                break
            for key, value in sub_keys.items():
                number = string_parser.get_pct_value(key, self.release)
                log.output(f"[Found]: {key}")
                lenght_str = sum(1 for char in f"[{number}% match]:")
                formatting_spaces = " " * lenght_str
                _name = f"[{number}% match]: {key}"
                _url = f"{formatting_spaces} {value}"
                to_be_sorted_value = number, _name, _url
                to_be_sorted.append(to_be_sorted_value)
                if self.check.is_threshold_met(key, self.title, self.season, self.episode, self.show_bool, number, self.pct):
                    to_be_downloaded.append(value) if value not in to_be_downloaded else None
            to_be_scraped.pop(0) if len(to_be_scraped) > 0 else None
            sorted_list = log_and_sort_list(to_be_sorted, self.pct)
            log.output("Done with tasks")

        # exit if no subtitles found
        if len(to_be_downloaded) == 0:
            log.output("")
            log.output(f"No subtitles to download for {self.release}")
        if self.show_download_window and len(sorted_list) > 0 and len(to_be_downloaded) == 0:
            file = f"{__video_directory__}\\__subsearch__dl_data.tmp"
            with open(file, "w", encoding="utf8") as f:
                for i in range(len(sorted_list)):
                    name, _link = sorted_list[i][1], sorted_list[i][2]
                    link = _link.replace(" ", "")
                    f.writelines(f"{name} {link}")
                    f.write("\n")

            return None

        download_info = []
        tbd_lenght = len(to_be_downloaded)
        for zip_idx, download_url in enumerate(to_be_downloaded, start=1):
            zip_url = self.scrape.download_url(download_url)
            zip_fp = f"{__video_directory__}\\__subsearch__subscene_{zip_idx}.zip"
            data = SubsceneData(file_path=zip_fp, url=zip_url, idx_num=zip_idx, idx_lenght=tbd_lenght)
            download_info.append(data)
        return download_info


class SubsceneScrape:
    def __init__(self):
        self.check = SubsceneChecks()

    def title(self, url: str) -> dict[str, str]:
        titles: dict[str, str] = {}
        doc = get_lxml_doc(url)
        tag_div = doc.find("div", class_="search-result")
        self.check.is_captcha(tag_div)
        tag_div = tag_div.find_all("div", class_="title")
        for class_title in tag_div:
            title_name = class_title.contents[1].contents[0].strip().replace(":", "")
            title_url = class_title.contents[1].attrs["href"]
            titles[title_name] = f"https://subscene.com{title_url}"
        return titles

    def subtitle(self, language: str, hearing_impaired: bool | str, url: str) -> dict[str, str]:
        subtitles: dict[str, str] = {}
        doc = get_lxml_doc(url)
        tag_tbody = doc.find("tbody")
        while tag_tbody is None:
            self.check.to_many_requests(tag_tbody)
            tag_tbody = doc.find("tbody")
        tag_td = tag_tbody.find_all("td", class_="a1")
        for class_a1 in tag_td:
            sub_hi = self.check.is_subtitle_hearing_impaired(class_a1)
            subtitle_language = class_a1.contents[1].contents[1].contents[0].strip()
            if hearing_impaired != "Both" and hearing_impaired != sub_hi:
                continue
            if language != subtitle_language:
                continue
            release_name = class_a1.contents[1].contents[3].string.strip()
            release_name = release_name.replace(" ", ".")
            subtitle_url = class_a1.contents[1].attrs["href"]
            subtitles[release_name] = f"https://subscene.com{subtitle_url}"
        return subtitles

    def download_url(self, url: str) -> str:
        source = SCRAPER.get(url).text
        doc = BeautifulSoup(source, "lxml")
        button_url = [dl["href"] for dl in doc.find_all("a", href=True, id="downloadButton")]
        download_url = f"https://subscene.com/{button_url[0]}"
        return download_url


class SubsceneChecks:
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

    def is_show_bool(self, key: str, title: str, season_ordinal: str, show_bool: bool, lang_code2: str) -> bool:
        if title and season_ordinal in key.lower() and show_bool and lang_code2:
            log.output(f"TV-Series {key} found")
            return True
        return False

    def is_threshold_met(
        self, key: str, title: str, season: str, episode: str, show_bool: bool, number: int, pct: int
    ) -> bool:
        if number >= pct or title and f"{season}{episode}" in key.lower() and show_bool:
            return True
        return False

    def is_subtitle_hearing_impaired(self, a1: Tag) -> bool:
        a1_parent = a1.parent
        class_a40 = a1_parent.find("td", class_="a40")  # non-hearing impaired
        class_a41 = a1_parent.find("td", class_="a41")  # hearing imparted
        if class_a40 is None:
            return True
        elif class_a41 is None:
            return False

    def to_many_requests(body: Tag):
        sec = time.sleep(1)
        log.output(f"ToManyRequestsWarning: To many requests, sleept for {sec}s")

    def is_captcha(self, doc: Tag):
        tag_h2 = doc.find("h2", text="Why do I have to complete a CAPTCHA?")
        if tag_h2 is not None:
            raise CaptchaError("Captcha protection detected. Please try again later.")
