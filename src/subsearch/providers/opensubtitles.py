import re
from typing import Union

from subsearch.data import __video__
from subsearch.providers import generic
from subsearch.providers.generic import BaseProvider, FormattedData
from subsearch.utils import log, string_parser
from subsearch.utils.raw_config import UserParameters
from subsearch.utils.string_parser import FileSearchParameters


class OpenSubtitles(BaseProvider):
    def __init__(self, parameters: FileSearchParameters, user_parameters: UserParameters):
        BaseProvider.__init__(self, parameters, user_parameters)
        self.scrape = OpenSubtitlesScrape()
        self.logged_and_sorted: list[FormattedData] = []

    def parse_hash_results(self):
        to_be_downloaded = self.scrape.with_hash(self.url_opensubtitles_hash, self.release)
        if to_be_downloaded is None and self.series:
            log.output(f"No TV-series found matching hash {self.file_hash}")
            log.output(f"Done with tasks\n")
            return None
        if to_be_downloaded is None:
            log.output(f"No movies found matching hash {self.file_hash}")
            log.output(f"Done with tasks\n")
            return None
        log.output(f"[100%  match]: {self.release}")
        download_info = generic.named_tuple_zip_data("opensubtitles", __video__.tmp_directory, to_be_downloaded)
        log.output(f"Done with tasks\n")
        return download_info

    def parse_site_results(self):
        to_be_sorted = []
        subtitle_data = self.scrape.get_subtitles(self.url_opensubtitles)
        to_be_downloaded: dict[str, str] = {}
        to_be_sorted: list[FormattedData] = []
        for key, value in subtitle_data.items():
            pct_result = string_parser.get_pct_value(key, self.release)
            log.output(f"[{pct_result:>3}%  match]: {key}")
            formatted_data = generic.format_key_value_pct("opensubtitles", key, value, pct_result)
            to_be_sorted.append(formatted_data)
            if self.is_threshold_met(key, pct_result) is False:
                continue
            if value in to_be_downloaded.values():
                continue
            to_be_downloaded[key] = value
        self.logged_and_sorted = generic.log_and_sort_list("opensubtitles", to_be_sorted, self.pct_threashold)
        # exit if no subtitles found
        if len(to_be_downloaded) == 0:
            log.output(f"No subtitles to download for {self.release}")
            log.output("Done with tasks\n")
            return None

        download_info = generic.named_tuple_zip_data("opensubtitles", __video__.tmp_directory, to_be_downloaded)
        log.output("Done with tasks\n")
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

    def with_hash(self, url: str, release: str) -> dict[str, str] | None:
        subtitles: dict[str, str] = {}
        doc = generic.get_lxml_doc(url, "lxml")
        doc_results = doc.find("a", download="download", id="bt-dwl-bt")
        if doc_results is None:
            return None
        sub_id = doc_results.attrs["data-product-id"]
        download_url = f"https://dl.opensubtitles.org/en/download/sub/{sub_id}"
        subtitles[release] = download_url
        return subtitles
