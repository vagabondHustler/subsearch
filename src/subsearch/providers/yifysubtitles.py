from selectolax.parser import Node

from subsearch.globals.dataclasses import Subtitle
from subsearch.providers import common_utils


class YifySubtitlesScraper(common_utils.ProviderHelper):
    def __init__(self, **kwargs) -> None:
        common_utils.ProviderHelper.__init__(self, **kwargs)

    def skip_item(self, item: Node, hi_sub: bool, regular_sub: bool, current_language: str) -> bool:
        subtitle_language = item.css_first("span.sub-lang").child.text_content  # type: ignore
        hearing_impaired = item.css_matches("span.hi-subtitle")
        if subtitle_language.lower() != current_language.lower():  # type: ignore
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
        tree = common_utils.get_html_parser(url)
        product = tree.select("tr")
        for item in product.matches[1:]:  # type: ignore
            if self.skip_item(item, hi_sub, non_hi_sub, current_language):
                continue
            node = item.css_first("a")
            titles = node.text().strip().split("subtitle ")[-1].split("\n")
            _href = node.attributes["href"].split("/")  # type: ignore
            href = _href[-1]
            for title in titles:
                subtitles[title] = f"https://yifysubtitles.org/subtitle/{href}.zip"
        return subtitles


class YifiSubtitles(YifySubtitlesScraper):
    def __init__(self, **kwargs) -> None:
        YifySubtitlesScraper.__init__(self, **kwargs)
        self.provider_name = self.__class__.__name__.lower()

    def start_search(self, **kwargs) -> list[Subtitle] | None:
        subtitle_data = self.get_subtitle(self.url_yifysubtitles, self.current_language, self.hi_sub, self.non_hi_sub)

        if not subtitle_data:
            return []

        self._process_subtitle_data(self.provider_name, subtitle_data)

    @property
    def accepted_subtitles(self) -> list[Subtitle]:
        return self._accepted_subtitles

    @property
    def rejected_subtitles(self) -> list[Subtitle]:
        return self._rejected_subtitles
