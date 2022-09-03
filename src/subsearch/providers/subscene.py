from bs4 import BeautifulSoup

from subsearch.data import __video__
from subsearch.providers import generic
from subsearch.providers.generic import SCRAPER, BaseChecks, BaseProvider, DownloadData
from subsearch.utils import log, string_parser
from subsearch.utils.raw_config import UserParameters
from subsearch.utils.string_parser import FileSearchParameters


class Subscene(BaseProvider):
    def __init__(self, parameters: FileSearchParameters, user_parameters: UserParameters):
        BaseProvider.__init__(self, parameters, user_parameters)
        self.scrape = SubsceneScrape()
        self.check = BaseChecks()

    def parse(self):
        to_be_scraped: list[str] = []
        definitive_match = self.url_subscene.rsplit("query=", 1)[-1].replace("%20", " ")
        title_keys = self.scrape.title(self.url_subscene, definitive_match)
        for key, value in title_keys.items():
            if self.check.is_movie(key, self.title, self.year):
                to_be_scraped.append(value) if value not in (to_be_scraped) else None
            if self.check.try_the_year_before(key, self.title, self.year):
                to_be_scraped.append(value) if value not in (to_be_scraped) else None
            if self.check.is_series(key, self.title, self.season_ordinal, self.series):
                to_be_scraped.append(value) if value not in (to_be_scraped) else None
        log.output("Done with task\n") if len(to_be_scraped) > 0 else None

        # exit if no titles found
        if len(to_be_scraped) == 0:
            if self.series:
                log.output(f"\nNo TV-series found matching {self.title}")
            else:
                log.output(f"\nNo movies found matching {self.title}")
            return None

        # search title for subtitles
        to_be_downloaded: dict[str, str] = {}
        to_be_sorted: list[tuple[int, str, str]] = []
        while len(to_be_scraped) > 0:
            for subtitle_url in to_be_scraped:
                log.output(f"[Searching for on subscene - subtitle]")
                sub_keys = self.scrape.subtitle(self.current_language, self.hearing_impaired, subtitle_url)
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
                if self.check.is_threshold_met(key, self.title, self.season, self.episode, self.series, number, self.pct):
                    to_be_downloaded[key] = value if key not in to_be_downloaded else None
            to_be_scraped.pop(0) if len(to_be_scraped) > 0 else None
            self._sorted_list = generic.log_and_sort_list("subscene", to_be_sorted, self.pct)
        # exit if no subtitles found
        if len(to_be_downloaded) == 0:
            log.output(f"No subtitles to download for {self.release}")
            log.output("Done with tasks\n")
            return None

        download_info = []
        tbd_lenght = len(to_be_downloaded)
        for zip_idx, (zip_name, _zip_url) in enumerate(to_be_downloaded.items(), start=1):
            zip_url = self.scrape.download_url(_zip_url)
            zip_fp = f"{__video__.directory}\\__subsearch__subscene_{zip_idx}.zip"
            data = DownloadData(name=zip_name, file_path=zip_fp, url=zip_url, idx_num=zip_idx, idx_lenght=tbd_lenght)
            download_info.append(data)
        log.output("Done with tasks\n")
        return download_info

    def sorted_list(self):
        return self._sorted_list


class SubsceneScrape:
    def __init__(self):
        self.check = BaseChecks()

    def title(self, url: str, definitive_match: str) -> dict[str, str]:
        titles: dict[str, str] = {}
        doc = generic.get_lxml_doc(url)
        tag_div = doc.find("div", class_="search-result")
        self.check.is_captcha(tag_div)
        tag_div = tag_div.find_all("div", class_="title")
        for class_title in tag_div:
            title_name = class_title.contents[1].contents[0].strip().replace(":", "")
            title_url = class_title.contents[1].attrs["href"]
            titles[title_name] = f"https://subscene.com{title_url}"
            if title_name.lower() == definitive_match:
                break
        return titles

    def subtitle(self, current_language: str, hearing_impaired: bool | str, url: str) -> dict[str, str]:
        subtitles: dict[str, str] = {}
        doc = generic.get_lxml_doc(url)
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
            if current_language.lower() != subtitle_language.lower():
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
