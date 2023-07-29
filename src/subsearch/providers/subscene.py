from selectolax.parser import Node

from subsearch.data.data_classes import Subtitle
from subsearch.providers import core_provider


class SubsceneScraper(core_provider.ProviderHelper):
    def __init__(self, **kwargs) -> None:
        core_provider.ProviderHelper.__init__(self, **kwargs)

    def find_title(self, url: str, current_language: str, definitive_match: list[str]) -> str | None:
        tree = core_provider.get_html_parser(url)
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

    def find_subtitles(self, url: str, hi_sub: bool, regular_sub: bool, subscene_header) -> dict[str, str]:
        subtitles: dict[str, str] = {}
        tree = core_provider.get_html_parser(url, subscene_header)
        products = tree.css("tr")
        for item in products[1:]:
            if self.skip_item(item, hi_sub, regular_sub):
                continue
            node = item.css_first("a")
            if node.child.text_content == "upload":
                continue
            subtitle_href = node.attributes["href"]
            filename = item.css_first("span:nth-child(2)").child.text_content.strip()
            subtitles[filename] = f"https://subscene.com{subtitle_href}"
        return subtitles


class Subscene(SubsceneScraper):
    def __init__(self, **kwargs):
        SubsceneScraper.__init__(self, **kwargs)
        self.provider_name = self.__class__.__name__.lower()

    def start_search(self):
        custom_subscene_header = core_provider.CustomSubsceneHeader(self.app_config)
        header = custom_subscene_header.create_header()
        definitive_match = self._definitive_match()
        found_title_url = self.find_title(self.url_subscene, self.current_language, definitive_match)

        if not found_title_url:
            return []

        subtitle_data = self.find_subtitles(found_title_url, self.hi_sub, self.non_hi_sub, header)
        self._process_subtitle_data(self.provider_name, subtitle_data)

    def _definitive_match(self) -> list[str]:
        if self.tvseries:
            return [f"{self.title} - {self.season_ordinal} season"]
        return [f"{self.title} ({self.year})", f"{self.title} ({(self.year-1)})"]

    @property
    def accepted_subtitles(self) -> list[Subtitle]:
        return self._accepted_subtitles

    @property
    def rejected_subtitles(self) -> list[Subtitle]:
        return self._rejected_subtitles
