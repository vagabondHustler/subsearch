from typing import Any

from selectolax.lexbor import LexborNode

from subsearch.io import http
from subsearch.providers import provider_helper
from subsearch.runtime.models.model import ProviderHealth


class YifySubtitlesScraper(provider_helper.ProviderHelper):
    def __init__(self, *args, **kwargs) -> None:
        provider_helper.ProviderHelper.__init__(self, *args, **kwargs)
        self.provider_name = ""

    def response_is_well_formed(self, tree: Any) -> bool:
        return tree.css_first("table") is not None

    def get_subtitles(self) -> ProviderHealth:
        tree = http.request_parsed_response(url=self.url_yifysubtitles, timeout=self.request_timeout)
        if not tree:
            return ProviderHealth.NO_RESPONSE
        if not self.response_is_well_formed(tree):
            return ProviderHealth.STRUCTURE_INVALID

        product = tree.select("tr")
        for item in product.matches[1:]:  # type: ignore
            reason = self.skip_reason(item)
            if reason:
                self.record_filtered_out(self.provider_name, self._item_name(item), reason)
                continue
            self.parse_item(item)
        return ProviderHealth.OK

    def _item_name(self, item: LexborNode) -> str:
        node = item.css_first("a")
        return node.text().strip() if node else ""

    def parse_item(self, item) -> None:
        node = item.css_first("a")
        titles = node.text().strip().split("subtitle ")[-1].split("\n")
        _href = node.attributes["href"].split("/")  # type: ignore
        href = _href[-1]
        download_url = f"https://yifysubtitles.org/subtitle/{href}.zip"
        for subtitle_name in titles:
            self.prepare_subtitle(self.provider_name, subtitle_name, download_url, {})

    def skip_reason(self, item: LexborNode) -> str:
        subtitle_language = item.css_first("span.sub-lang").child.text_content  # type: ignore
        subtitle_hi = item.css_matches("span.hi-subtitle")
        if subtitle_language.lower() != self.current_language.lower():  # type: ignore
            return "language"
        if not self.subtitle_hi_match(subtitle_hi):
            return "hi"
        return ""


class YifySubtitles(YifySubtitlesScraper):
    def __init__(self, *args, **kwargs) -> None:
        YifySubtitlesScraper.__init__(self, *args, **kwargs)
        self.provider_name = self.__class__.__name__.lower()

    def start_search(self, *args, **kwargs) -> None:
        self.run_search(self.get_subtitles)
