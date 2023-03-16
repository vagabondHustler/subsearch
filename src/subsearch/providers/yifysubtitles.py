from selectolax.parser import Node

from subsearch.data import video_data
from subsearch.data.data_objects import (
    AppConfig,
    DownloadMetaData,
    FormattedMetadata,
    ProviderUrls,
    ReleaseData,
)
from subsearch.providers import generic
from subsearch.providers.generic import ProviderParameters
from subsearch.utils import log, string_parser


class YifySubtitlesScraper:
    def __init__(self) -> None:
        ...

    def skip_item(self, item: Node, hi_sub: bool, regular_sub: bool, current_language: str) -> bool:
        subtitle_language = item.css_first("span.sub-lang").child.text_content
        hearing_impaired = item.css_matches("span.hi-subtitle")
        if subtitle_language.lower() != current_language.lower():
            return True
        if (hi_sub and regular_sub) or (hi_sub is False and regular_sub is False):
            pass
        elif hi_sub is False and hearing_impaired:
            return True
        elif regular_sub is True and hearing_impaired:
            return True
        return False

    def get_subtitle(self, url: str, current_language: str, hi_sub: bool, non_hi_sub: bool) -> dict[str, str]:
        subtitles: dict[str, str] = {}
        tree = generic.get_html_parser(url)
        product = tree.select("tr")
        for item in product.matches[1:]:
            if self.skip_item(item, hi_sub, non_hi_sub, current_language):
                continue
            node = item.css_first("a")
            titles = node.text().strip().split("subtitle ")[-1].split("\n")
            _href = node.attributes["href"].split("/")
            href = _href[-1]
            for title in titles:
                subtitles[title] = f"https://yifysubtitles.org/subtitle/{href}.zip"
        return subtitles


class YifiSubtitles(ProviderParameters, YifySubtitlesScraper):
    def __init__(self, **kwargs):
        ProviderParameters.__init__(self, **kwargs)
        YifySubtitlesScraper.__init__(self)
        self.logged_and_sorted: list[FormattedMetadata] = []

    def parse_site_results(self) -> list | list[DownloadMetaData]:
        # search for title
        subtitle_data = self.get_subtitle(self.url_yifysubtitles, self.current_language, self.hi_sub, self.non_hi_sub)
        to_be_downloaded: dict[str, str] = {}
        to_be_sorted: list[FormattedMetadata] = []

        data_found = True if subtitle_data else False
        if data_found is False:
            return []
        # search for subtitle
        for key, value in subtitle_data.items():
            pct_result = string_parser.calculate_match(key, self.release)
            log.output_match("yifysubtitles", pct_result, key)
            formatted_data = generic.format_key_value_pct("yifysubtitles", key, value, pct_result)
            to_be_sorted.append(formatted_data)
            if self.is_threshold_met(key, pct_result) is False or self.manual_download_mode:
                continue
            if value in to_be_downloaded.values():
                continue
            to_be_downloaded[key] = value

        self.sorted_metadata = generic.sort_download_metadata(to_be_sorted)
        log.downlod_metadata("yifysubtitles", self.sorted_metadata, self.percentage_threashold)

        if not to_be_downloaded:
            return []

        # pack download data
        download_info = generic.pack_download_data("yifysubtitles", video_data.tmp_directory, to_be_downloaded)
        return download_info

    def _sorted_list(self) -> list[FormattedMetadata]:
        return self.sorted_metadata
