from selectolax.parser import Node

from subsearch.data import video_data
from subsearch.data.data_objects import DownloadMetaData, FormattedMetadata
from subsearch.providers import generic
from subsearch.providers.generic import ProviderParameters
from subsearch.utils import log, string_parser


class SubsceneScraper:
    def __init__(self) -> None:
        ...

    def find_title(self, url: str, current_language: str, definitive_match: list[str]) -> str | None:
        tree = generic.get_html_parser(url)
        products = tree.css("div.title")
        for item in products:
            node = item.css_first("a")
            result_href = node.attributes["href"]
            result_title = str(node.child.html).lower()
            if result_title not in definitive_match:
                continue
            current_language = current_language.lower()
            return f"https://subscene.com{result_href}/{current_language}"

    def skip_item(self, item: Node, hi_sub: bool, regular_sub: bool) -> bool:
        if item.css_matches("td.banner-inlist"):
            return True
        if (hi_sub and regular_sub) or (hi_sub is False and regular_sub is False):
            pass
        elif hi_sub is False and item.css_matches("td.a40"):
            return True
        elif regular_sub is False and item.css_matches("td.a41"):
            return True
        return False

    def find_subtitles(self, url: str, hi_sub: bool, regular_sub: bool) -> dict[str, str]:
        subtitles: dict[str, str] = {}
        tree = generic.get_html_parser(url)
        products = tree.css("tr")
        for item in products[1:]:
            if self.skip_item(item, hi_sub, regular_sub):
                continue
            node = item.css_first("a")
            subtitle_href = node.attributes["href"]
            filename = item.css_first("span:nth-child(2)").child.text_content.strip()
            subtitles[filename] = f"https://subscene.com{subtitle_href}"
        return subtitles

    def get_download_url(self, url: str) -> str:
        tree = generic.get_html_parser(url)
        href = tree.css_first("#downloadButton").attributes["href"]
        download_url = f"https://subscene.com/{href}"
        return download_url


class Subscene(ProviderParameters, SubsceneScraper):
    def __init__(self, **kwargs):
        ProviderParameters.__init__(self, **kwargs)
        SubsceneScraper.__init__(self)
        self.logged_and_sorted: list[FormattedMetadata] = []

    def _definitive_match(self) -> list[str]:
        if self.tvseries:
            return [f"{self.title} - {self.season_ordinal} season"]
        return [f"{self.title} ({self.year})", f"{self.title} ({(self.year-1)})"]

    def parse_site_results(self) -> list | list[DownloadMetaData]:
        to_be_sorted: list[FormattedMetadata] = []
        _to_be_downloaded: dict[str, str] = {}
        to_be_downloaded: dict[str, str] = {}

        # find title
        definitive_match = self._definitive_match()
        found_title_url = self.find_title(self.url_subscene, self.current_language, definitive_match)
        if not found_title_url:
            return []

        # search for subtitles
        subtitle_data = self.find_subtitles(found_title_url, self.hi_sub, self.non_hi_sub)
        for key, value in subtitle_data.items():
            pct_result = string_parser.calculate_match(key, self.release)
            log.output_match("subscene", pct_result, key)
            formatted_data = generic.format_key_value_pct("subscene", key, value, pct_result)
            to_be_sorted.append(formatted_data)
            if self.is_threshold_met(key, pct_result) is False or self.manual_download_mode:
                continue
            if key in _to_be_downloaded.keys():
                continue
            _to_be_downloaded[key] = value

        self.sorted_metadata = generic.sort_download_metadata(to_be_sorted)
        log.downlod_metadata("subscene", self.sorted_metadata, self.percentage_threashold)
        if not _to_be_downloaded:
            return []

        # gather subtitle download url
        for release, subtitle_url in _to_be_downloaded.items():
            zip_url = self.get_download_url(subtitle_url)
            to_be_downloaded[release] = zip_url

        if not to_be_downloaded:
            return []

        # pack download data
        download_info = generic.pack_download_data("subscene", video_data.tmp_directory, to_be_downloaded)
        return download_info

    def _sorted_list(self) -> list[FormattedMetadata]:
        return self.sorted_metadata
