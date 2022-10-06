import re

from subsearch.data import __video__
from subsearch.data.data_fields import (
    FormattedData,
    ProviderUrlData,
    ReleaseData,
    UserData,
)
from subsearch.providers import generic
from subsearch.providers.generic import BaseProvider
from subsearch.utils import log, string_parser


class OpenSubtitles(BaseProvider):
    def __init__(self, parameters: ReleaseData, user_parameters: UserData, provider_url: ProviderUrlData):
        BaseProvider.__init__(self, parameters, user_parameters, provider_url)
        self.scrape = OpenSubtitlesScrape()
        self.logged_and_sorted: list[FormattedData] = []

    def parse_hash_results(self):
        # search for hash
        to_be_downloaded = self.scrape.with_hash(self.url_opensubtitles_hash, self.release)

        # log results
        data_found = True if to_be_downloaded else False
        log.output_title_data_result(data_found, from_hash=True)
        if data_found is False:
            return []
        log.output_match(100, self.release)

        # pack download data
        download_info = generic.pack_download_data("opensubtitles", __video__.tmp_directory, to_be_downloaded)
        return download_info

    def parse_site_results(self):
        # search for title
        to_be_sorted = []
        subtitle_data = self.scrape.get_subtitles(self.url_opensubtitles)

        # log results
        data_found = True if subtitle_data else False
        log.output_title_data_result(data_found)
        if data_found is False:
            return []

        # search for subtitle
        to_be_downloaded: dict[str, str] = {}
        to_be_sorted: list[FormattedData] = []
        for key, value in subtitle_data.items():
            pct_result = string_parser.get_pct_value(key, self.release)
            log.output_match(pct_result, key)
            formatted_data = generic.format_key_value_pct("opensubtitles", key, value, pct_result)
            to_be_sorted.append(formatted_data)
            if self.is_threshold_met(key, pct_result) is False:
                continue
            if value in to_be_downloaded.values():
                continue
            to_be_downloaded[key] = value

        self.logged_and_sorted = generic.log_and_sort_list("opensubtitles", to_be_sorted, self.pct_threashold)
        log.output_subtitle_result(to_be_downloaded, to_be_sorted)
        if not to_be_downloaded:
            return []

        # pack download data
        download_info = generic.pack_download_data("opensubtitles", __video__.tmp_directory, to_be_downloaded)
        return download_info

    def _sorted_list(self):
        return self.logged_and_sorted


class OpenSubtitlesScrape(OpenSubtitles):
    def __init__(self):
        ...

    def get_subtitles(self, url: str):
        subtitles: dict[str, str] = {}
        doc = generic.get_lxml_doc(url, "xml")
        items = doc.find_all("item")
        for item in items:
            dl_url = item.enclosure["url"]
            released_as = item.description.text.strip()
            release_name = re.findall("^.*?: (.*?);", released_as)[0]  # https://regex101.com/r/LWAmJK/1
            subtitles[release_name] = dl_url
        return subtitles

    def with_hash(self, url: str, release: str) -> dict[str, str]:
        subtitles: dict[str, str] = {}
        doc = generic.get_lxml_doc(url, "lxml")
        doc_results = doc.find("a", download="download", id="bt-dwl-bt")
        if doc_results is None:
            return subtitles
        sub_id = doc_results.attrs["data-product-id"]
        download_url = f"https://dl.opensubtitles.org/en/download/sub/{sub_id}"
        subtitles[release] = download_url
        return subtitles
