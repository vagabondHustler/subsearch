import re
from typing import Any

from subsearch.data import video_data
from subsearch.data.data_objects import DownloadMetaData, FormattedMetadata
from subsearch.providers import generic
from subsearch.providers.generic import ProviderParameters
from subsearch.utils import log, string_parser


class OpenSubtitlesScraper:
    def __init__(self) -> None:
        ...

    def opensubtitles_down(self, tree: Any):
        is_offline = tree.css_matches("pre")
        if is_offline is False:
            return False
        offline_text = tree.css_first("pre").text()
        if offline_text.startswith("Site will be online soon"):
            log.output(f"opensubtitles is down: {offline_text}", level="warning")
            return True
        return False

    def get_subtitles(self, url: str):
        subtitles: dict[str, str] = {}
        tree = generic.get_html_parser(url)
        items = tree.css("item")
        if self.opensubtitles_down(tree):
            return subtitles
        for item in items:
            dl_url = item.css_first("enclosure").attributes["url"]
            released_as = item.css_first("description").child.text_content.strip()
            release_name = re.findall("^.*?: (.*?);", released_as)[0]  # https://regex101.com/r/LWAmJK/1
            subtitles[release_name] = dl_url
        return subtitles

    def with_hash(self, url: str, release: str) -> dict[str, str]:
        subtitles: dict[str, str] = {}
        tree = generic.get_html_parser(url)
        if self.opensubtitles_down(tree):
            return subtitles
        try:
            sub_id = tree.css_first("#bt-dwl-bt").attributes["data-product-id"]
        except AttributeError:
            return subtitles
        subtitles[release] = f"https://dl.opensubtitles.org/en/download/sub/{sub_id}"
        return subtitles


class OpenSubtitles(ProviderParameters, OpenSubtitlesScraper):
    def __init__(self, **kwargs):
        ProviderParameters.__init__(self, **kwargs)
        OpenSubtitlesScraper.__init__(self)
        self.logged_and_sorted: list[FormattedMetadata] = []

    def parse_hash_results(self) -> list | list[DownloadMetaData]:
        # search for hash
        to_be_downloaded = self.with_hash(self.url_opensubtitles_hash, self.release)

        # log results
        data_found = True if to_be_downloaded else False
        if data_found is False:
            return []
        log.output_match("opensubtitles", 100, self.release)

        # pack download data
        download_info = generic.pack_download_data("opensubtitles", video_data.tmp_directory, to_be_downloaded)
        return download_info

    def parse_site_results(self) -> list | list[DownloadMetaData]:
        # search for title
        subtitle_data = self.get_subtitles(self.url_opensubtitles)

        # log results
        data_found = True if subtitle_data else False
        if data_found is False:
            return []

        # search for subtitle
        to_be_downloaded: dict[str, str] = {}
        to_be_sorted: list[FormattedMetadata] = []
        for key, value in subtitle_data.items():
            pct_result = string_parser.calculate_match(key, self.release)
            log.output_match("opensubtitles", pct_result, key)
            formatted_data = generic.format_key_value_pct("opensubtitles", key, value, pct_result)
            to_be_sorted.append(formatted_data)
            if self.is_threshold_met(key, pct_result) is False or self.manual_download_mode:
                continue
            if value in to_be_downloaded.values():
                continue
            to_be_downloaded[key] = value

        self.sorted_metadata = generic.sort_download_metadata(to_be_sorted)
        log.downlod_metadata("opensubtitles", self.sorted_metadata, self.percentage_threashold)

        if not to_be_downloaded:
            return []

        # pack download data
        download_info = generic.pack_download_data("opensubtitles", video_data.tmp_directory, to_be_downloaded)
        return download_info

    def _sorted_list(self) -> list[FormattedMetadata]:
        return self.sorted_metadata
