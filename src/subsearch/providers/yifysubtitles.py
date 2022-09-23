from subsearch.data import __video__
from subsearch.data.data_fields import (
    FileSearchData,
    FormattedData,
    ProviderUrlData,
    UserConfigData,
)
from subsearch.providers import generic
from subsearch.providers.generic import BaseProvider
from subsearch.utils import log, string_parser


class YifiSubtitles(BaseProvider):
    def __init__(self, parameters: FileSearchData, user_parameters: UserConfigData, provider_url: ProviderUrlData):
        BaseProvider.__init__(self, parameters, user_parameters, provider_url)
        self.scrape = YifySubtitlesScrape()
        self.logged_and_sorted: list[FormattedData] = []

    def parse_site_results(self):
        subtitle_data = self.scrape.get_subtitle(self.url_yifysubtitles, self.current_language)
        to_be_downloaded: dict[str, str] = {}
        to_be_sorted: list[FormattedData] = []
        for key, value in subtitle_data.items():
            pct_result = string_parser.get_pct_value(key, self.release)
            self.log.match(pct_result, key)
            formatted_data = generic.format_key_value_pct("yifysubtitles", key, value, pct_result)
            to_be_sorted.append(formatted_data)
            if self.is_threshold_met(key, pct_result) is False:
                continue
            if value in to_be_downloaded.values():
                continue
            to_be_downloaded[key] = value
        self.logged_and_sorted = generic.log_and_sort_list("yifysubtitles", to_be_sorted, self.pct_threashold)

        if not to_be_downloaded:
            self.log.no_subtitles_found(self.release)
            return None

        download_info = generic.pack_download_data("yifysubtitles", __video__.tmp_directory, to_be_downloaded)
        self.log.done_with_tasks(end_new_line=True)
        return download_info

    def _sorted_list(self):
        return self.logged_and_sorted


class YifySubtitlesScrape(YifiSubtitles):
    def __init__(self):
        ...

    def get_subtitle(self, url: str, current_language: str) -> dict[str, str]:
        doc = generic.get_lxml_doc(url)
        tag_tbody = doc.find("tbody")
        subtitles: dict[str, str] = {}
        if tag_tbody is None:
            return subtitles
        tbody_content = tag_tbody.contents[1::2]
        for class_a1 in tbody_content:
            subtitle_language = class_a1.contents[3].text
            if current_language.lower() != subtitle_language.lower():
                continue
            _releases = class_a1.contents[5].contents[1].contents[3::2]
            _releases_stripped = list(map(lambda release: release.strip(), _releases))
            _releases_no_space = list(map(lambda release: release.replace(" ", "."), _releases_stripped))
            _release_lower = list(map(lambda release: release.lower(), _releases_no_space))
            for release in _release_lower:
                subtitle_url = class_a1.contents[5].contents[1].attrs["href"].replace("subtitles", "subtitle")
                subtitles[release] = f"https://yifysubtitles.org{subtitle_url}.zip"
        return subtitles
