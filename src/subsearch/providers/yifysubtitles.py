from concurrent.futures import ThreadPoolExecutor
from typing import Any
from urllib.parse import urlsplit

from selectolax.lexbor import LexborHTMLParser, LexborNode

from subsearch.io import http
from subsearch.providers import provider_helper
from subsearch.runtime.models import ProviderDiagnosticStatus
from subsearch.runtime.recorder import LogLevel, capture


class YifySubtitlesScraper(provider_helper.ProviderHelper):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        provider_helper.ProviderHelper.__init__(self, *args, **kwargs)
        self.provider_name = ""
        self.download_domain = ""
        self.any_mirror_responded = False

    def response_is_well_formed(self, tree: Any) -> bool:
        return tree.css_first("table") is not None

    def _select_responding_mirror(self) -> tuple[LexborHTMLParser, str] | None:
        self.any_mirror_responded = False
        for url in self.provider_urls.yifysubtitles:
            capture(f"{self.provider_name}: trying mirror {url}", level=LogLevel.DEBUG)
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
                capture(
                    f"{self.provider_name}: mirror responded but page structure was invalid",
                    level=LogLevel.WARNING,
                )
                return ProviderDiagnosticStatus.STRUCTURE_INVALID
            capture(f"{self.provider_name}: no mirror responded", level=LogLevel.WARNING)
            return ProviderDiagnosticStatus.NO_RESPONSE
        tree, responding_url = selected
        split_url = urlsplit(responding_url)
        self.download_domain = f"{split_url.scheme}://{split_url.netloc}"

        product = tree.select("tr")
        accepted_items = []
        for item in product.matches[1:]:  # type: ignore
            reason = self.skip_reason(item)
            if reason:
                self.record_filtered_out(self.provider_name, self._item_name(item), reason)
                continue
            accepted_items.append(item)

        page_urls = [f"{self.download_domain}{item.css_first('a').attributes['href']}" for item in accepted_items]  # type: ignore
        with ThreadPoolExecutor(max_workers=8) as executor:
            download_urls = list(executor.map(self._resolve_download_url, page_urls))

        for item, page_url, download_url in zip(accepted_items, page_urls, download_urls):
            self.parse_item(item, page_url, download_url)
        return ProviderDiagnosticStatus.OK

    def _item_name(self, item: LexborNode) -> str:
        node = item.css_first("a")
        return node.text().strip() if node else ""

    def parse_item(self, item: LexborNode, subtitle_page_url: str, download_url: str) -> None:
        if not download_url:
            capture(
                f"{self.provider_name}: no download link on {subtitle_page_url}",
                level=LogLevel.WARNING,
            )
            return
        titles = item.css_first("a").text().strip().split("subtitle ")[-1].split("\n")  # type: ignore
        download_headers = {"Referer": subtitle_page_url}
        for subtitle_name in titles:
            self.prepare_subtitle(self.provider_name, subtitle_name, download_url, {}, download_headers)

    def _resolve_download_url(self, subtitle_page_url: str) -> str:
        tree = http.request_parsed_response(url=subtitle_page_url, timeout=self.request_timeout)
        if not tree:
            return ""
        link = tree.css_first("a[href$='.zip']")
        if not link:
            return ""
        return f"{self.download_domain}{link.attributes['href']}"  # type: ignore

    def skip_reason(self, item: LexborNode) -> str:
        subtitle_language = item.css_first("span.sub-lang").child.text_content  # type: ignore
        subtitle_hi = item.css_matches("span.hi-subtitle")
        if subtitle_language.lower() != self.app_config.selected_language.lower():  # type: ignore
            return "language"
        if not self.subtitle_hi_match(subtitle_hi):
            return "hi"
        return ""


class YifySubtitles(YifySubtitlesScraper):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        YifySubtitlesScraper.__init__(self, *args, **kwargs)
        self.provider_name = self.__class__.__name__.lower()

    def start_search(self, *args: Any, **kwargs: Any) -> None:
        self.run_search(self.get_subtitles)
