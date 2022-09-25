from bs4 import BeautifulSoup

from subsearch.data import __video__
from subsearch.data.data_fields import (
    FormattedData,
    ProviderUrlData,
    ReleaseData,
    UserData,
)
from subsearch.providers import generic
from subsearch.providers.generic import SCRAPER, BaseProvider
from subsearch.utils import log, string_parser


class Subscene(BaseProvider):
    def __init__(self, parameters: ReleaseData, user_parameters: UserData, provider_url: ProviderUrlData):
        BaseProvider.__init__(self, parameters, user_parameters, provider_url)
        self.scrape = SubsceneScrape()
        self.logged_and_sorted: list[FormattedData] = []

    def parse_site_results(self):
        # search for title
        to_be_scraped: list[str] = []
        definitive_match = self.url_subscene.rsplit("query=", 1)[-1].replace("%20", " ")
        title_keys = self.scrape.get_title(self.url_subscene, definitive_match)
        for release, subtitle_url in title_keys.items():
            if self.is_movie(release):
                to_be_scraped.append(subtitle_url) if subtitle_url not in (to_be_scraped) else None
            if self.try_the_year_before(release):
                to_be_scraped.append(subtitle_url) if subtitle_url not in (to_be_scraped) else None
            if self.is_series(release):
                to_be_scraped.append(subtitle_url) if subtitle_url not in (to_be_scraped) else None

        # log results
        data_found = True if to_be_scraped else False
        log.output_title_data_result(data_found)
        if data_found is False:
            return []
        to_be_sorted: list[FormattedData] = []

        # search for subtitles
        for subtitle_url in to_be_scraped:
            subtitle_data = self.scrape.get_subtitle(self.current_language, self.hi_sub, self.non_hi_sub, subtitle_url)
            break

        _to_be_downloaded: dict[str, str] = {}
        for release, subtitle_url in subtitle_data.items():
            pct_result = string_parser.get_pct_value(release, self.release)
            log.output_match(pct_result, release)
            formatted_data = generic.format_key_value_pct("subscene", release, subtitle_url, pct_result)
            to_be_sorted.append(formatted_data)
            if self.is_threshold_met(release, pct_result) is False:
                continue
            if release in _to_be_downloaded.keys():
                continue
            _to_be_downloaded[release] = subtitle_url

        self.logged_and_sorted = generic.log_and_sort_list("subscene", to_be_sorted, self.pct_threashold)
        if not _to_be_downloaded:
            return []

        # gather subtitle download url
        to_be_downloaded: dict[str, str] = {}
        for release, subtitle_url in _to_be_downloaded.items():
            zip_url = self.scrape.get_download_url(subtitle_url)
            to_be_downloaded[release] = zip_url

        log.output_subtitle_result(to_be_downloaded, to_be_sorted)
        if not to_be_downloaded:
            return []

        # pack download data
        download_info = generic.pack_download_data("subscene", __video__.tmp_directory, to_be_downloaded)
        return download_info

    def _sorted_list(self):
        return self.logged_and_sorted


class SubsceneScrape(Subscene):
    def __init__(self):
        ...

    def get_title(self, url: str, definitive_match: str) -> dict[str, str]:
        titles: dict[str, str] = {}
        doc = generic.get_lxml_doc(url)
        tag_div = doc.find("div", class_="search-result")
        self.is_captcha(tag_div)
        tag_div = tag_div.find_all("div", class_="title")
        for class_title in tag_div:
            title_name = class_title.contents[1].contents[0].strip().replace(":", "")
            title_url = class_title.contents[1].attrs["href"]
            titles[title_name] = f"https://subscene.com{title_url}"
            if title_name.lower() == definitive_match:
                break
        return titles

    def get_subtitle(self, current_language: str, hi_sub: bool, regular_sub: bool, url: str) -> dict[str, str]:
        subtitles: dict[str, str] = {}
        doc = generic.get_lxml_doc(url)
        tag_tbody = doc.find("tbody")
        while tag_tbody is None:
            self.to_many_requests()
            tag_tbody = doc.find("tbody")
        tag_td = tag_tbody.find_all("td", class_="a1")
        for class_a1 in tag_td:
            is_sub_hi = self.is_subtitle_hearing_impaired(class_a1)
            subtitle_language = class_a1.contents[1].contents[1].contents[0].strip()
            if hi_sub and regular_sub is False and is_sub_hi is False:
                continue
            if hi_sub is False and regular_sub and is_sub_hi:
                continue
            if current_language.lower() != subtitle_language.lower():
                continue
            release_name = class_a1.contents[1].contents[3].string.strip()
            release_name = release_name.replace(" ", ".")
            subtitle_url = class_a1.contents[1].attrs["href"]
            subtitles[release_name] = f"https://subscene.com{subtitle_url}"
        return subtitles

    def get_download_url(self, url: str) -> str:
        source = SCRAPER.get(url).text
        doc = BeautifulSoup(source, "lxml")
        button_url = [dl["href"] for dl in doc.find_all("a", href=True, id="downloadButton")]
        download_url = f"https://subscene.com/{button_url[0]}"
        return download_url
