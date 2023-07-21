from selectolax.parser import Node

from subsearch.data.constants import APP_PATHS
from subsearch.data.data_classes import SkippedSubtitle, Subtitle
from subsearch.providers import core_provider
from subsearch.providers.core_provider import SearchArguments
from subsearch.utils import io_log, string_parser


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
        tree = core_provider.get_html_parser(url)
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


class YifiSubtitles(SearchArguments, YifySubtitlesScraper):
    def __init__(self, **kwargs):
        SearchArguments.__init__(self, **kwargs)
        YifySubtitlesScraper.__init__(self)
        self._accepted_subtitles: list[Subtitle] = []
        self._rejected_subtitles: list[Subtitle] = []
        self.provider_name = self.__class__.__name__.lower()

    def start_search(self) -> list | list[Subtitle]:
        subtitle_data = self.get_subtitle(self.url_yifysubtitles, self.current_language, self.hi_sub, self.non_hi_sub)

        if not subtitle_data:
            return None

        for subtitle_name, subtitle_url in subtitle_data.items():
            pct_result = string_parser.calculate_match(subtitle_name, self.release)
            io_log.stdout_match(
                provider=self.provider_name,
                subtitle_name=subtitle_name,
                result=pct_result,
                threshold=self.app_config.percentage_threshold,
            )
            if core_provider.is_threshold_met(self, pct_result):
                subtitle = Subtitle(pct_result, self.provider_name, subtitle_name.lower(), subtitle_url)
                self._accepted_subtitles.append(subtitle)
            else:
                subtitle = Subtitle(pct_result, self.provider_name, subtitle_name.lower(), subtitle_url)
                self._rejected_subtitles.append(subtitle)

    @property
    def accepted_subtitles(self) -> list[Subtitle]:
        return self._accepted_subtitles

    @property
    def rejected_subtitles(self) -> list[Subtitle]:
        return self._rejected_subtitles
