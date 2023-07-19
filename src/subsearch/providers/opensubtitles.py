import re
from typing import Any

from subsearch.data import app_paths
from subsearch.data.data_objects import DownloadData, PrettifiedDownloadData
from subsearch.providers import core_provider
from subsearch.providers.core_provider import SearchArguments
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
            log.stdout(f"opensubtitles is down: {offline_text}", level="error")
            return True
        return False

    def get_subtitles(self, url: str):
        subtitles: dict[str, str] = {}
        tree = core_provider.get_html_parser(url)
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
        tree = core_provider.get_html_parser(url)
        if self.opensubtitles_down(tree):
            return subtitles
        try:
            sub_id = tree.css_first("#bt-dwl-bt").attributes["data-product-id"]
        except AttributeError:
            return subtitles
        subtitles[release] = f"https://dl.opensubtitles.org/en/download/sub/{sub_id}"
        return subtitles


class OpenSubtitles(SearchArguments, OpenSubtitlesScraper):
    def __init__(self, **kwargs):
        SearchArguments.__init__(self, **kwargs)
        OpenSubtitlesScraper.__init__(self)
        self.logged_and_sorted: list[PrettifiedDownloadData] = []

    def parse_hash_results(self) -> list | list[DownloadData]:
        # search for hash
        to_be_downloaded = self.with_hash(self.url_opensubtitles_hash, self.release)

        # log results
        data_found = True if to_be_downloaded else False
        if data_found is False:
            return []
        log.stdout_match(
            provider="opensubtitles",
            subtitle_name=self.release,
            result=100,
            threshold=self.app_config.percentage_threshold,
        )

        # pack download data
        download_info = core_provider.set_download_data("opensubtitles", app_paths.tmpdir, to_be_downloaded)
        return download_info

    def parse_site_results(self) -> list | list[DownloadData]:
        # search for title
        subtitle_data = self.get_subtitles(self.url_opensubtitles)

        # log results
        data_found = True if subtitle_data else False
        if data_found is False:
            return []

        # search for subtitle
        to_be_downloaded: dict[str, str] = {}
        to_be_sorted: list[PrettifiedDownloadData] = []
        for key, value in subtitle_data.items():
            pct_result = string_parser.calculate_match(key, self.release)
            log.stdout_match(
                provider="opensubtitles",
                subtitle_name=key,
                result=pct_result,
                threshold=self.app_config.percentage_threshold,
            )
            formatted_data = core_provider.prettify_download_data("opensubtitles", key, value, pct_result)
            to_be_sorted.append(formatted_data)
            if core_provider.is_threshold_met(self, key, pct_result) is False or self.manual_download_mode:
                continue
            if value in to_be_downloaded.values():
                continue
            to_be_downloaded[key] = value

        self.sorted_site_results = core_provider.sort_site_results(to_be_sorted)

        if not to_be_downloaded:
            return []

        # pack download data
        download_info = core_provider.set_download_data("opensubtitles", app_paths.tmpdir, to_be_downloaded)
        return download_info

    def sorted_list(self) -> list[PrettifiedDownloadData]:
        return self.sorted_site_results
