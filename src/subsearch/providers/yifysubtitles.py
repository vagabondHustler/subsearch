from typing import Any
from urllib.parse import urlsplit

from selectolax.lexbor import LexborHTMLParser, LexborNode

from subsearch.io import http
from subsearch.providers import provider_helper
from subsearch.runtime.logging.events import LogEvent
from subsearch.runtime.logging.logger import log
from subsearch.runtime.models import ProviderDiagnosticStatus


class YifySubtitlesScraper(provider_helper.ProviderHelper):
    def __init__(self, *args, **kwargs) -> None:
        provider_helper.ProviderHelper.__init__(self, *args, **kwargs)
        self.provider_name = ""
        self.download_domain = ""
        self.any_mirror_responded = False

    def response_is_well_formed(self, tree: Any) -> bool:
        return tree.css_first("table") is not None

    def _select_responding_mirror(self) -> tuple[LexborHTMLParser, str] | None:
        self.any_mirror_responded = False
        for url in self.provider_urls.yifysubtitles:
            log.event(LogEvent.PROVIDER_MIRROR_TRIED, level="debug", provider=self.provider_name, url=url)
            tree = http.request_parsed_response(url=url, timeout=self.request_timeout)
            if not tree:
                continue
            self.any_mirror_responded = True
            if self.response_is_well_formed(tree):
                return tree, url
        return None

    def get_subtitles(self) -> ProviderDiagnosticStatus:
        selected = self._select_responding_mirror()
        if selected is None:
            if self.any_mirror_responded:
                log.event(LogEvent.PROVIDER_STRUCTURE_INVALID, level="warning", provider=self.provider_name)
                return ProviderDiagnosticStatus.STRUCTURE_INVALID
            log.event(LogEvent.PROVIDER_NO_MIRROR_RESPONDED, level="warning", provider=self.provider_name)
            return ProviderDiagnosticStatus.NO_RESPONSE
        tree, responding_url = selected
        split_url = urlsplit(responding_url)
        self.download_domain = f"{split_url.scheme}://{split_url.netloc}"

        product = tree.select("tr")
        for item in product.matches[1:]:  # type: ignore
            reason = self.skip_reason(item)
            if reason:
                self.record_filtered_out(self.provider_name, self._item_name(item), reason)
                continue
            self.parse_item(item)
        return ProviderDiagnosticStatus.OK

    def _item_name(self, item: LexborNode) -> str:
        node = item.css_first("a")
        return node.text().strip() if node else ""

    def parse_item(self, item) -> None:
        node = item.css_first("a")
        titles = node.text().strip().split("subtitle ")[-1].split("\n")
        _href = node.attributes["href"].split("/")  # type: ignore
        href = _href[-1]
        subtitle_page_url = f"{self.download_domain}/subtitle/{href}"
        download_url = f"{subtitle_page_url}.zip"
        download_headers = {"Referer": subtitle_page_url}
        for subtitle_name in titles:
            self.prepare_subtitle(self.provider_name, subtitle_name, download_url, {}, download_headers)

    def skip_reason(self, item: LexborNode) -> str:
        subtitle_language = item.css_first("span.sub-lang").child.text_content  # type: ignore
        subtitle_hi = item.css_matches("span.hi-subtitle")
        if subtitle_language.lower() != self.app_config.selected_language.lower():  # type: ignore
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
