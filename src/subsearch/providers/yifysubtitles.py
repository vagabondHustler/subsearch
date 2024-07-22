from selectolax.parser import Node

from subsearch.providers import common_utils


class YifySubtitlesScraper(common_utils.ProviderHelper):
    def __init__(self, *args, **kwargs) -> None:
        common_utils.ProviderHelper.__init__(self, *args, **kwargs)
        self.provider_name = ""

    def get_subtitles(self) -> None:
        tree = common_utils.request_parsed_response(url=self.url_yifysubtitles, timeout=self.request_timeout)
        if not tree:
            return None
        
        product = tree.select("tr")
        for item in product.matches[1:]:  # type: ignore
            if self.skip_item(item):
                continue
            self.parse_item(item)

    def parse_item(self, item) -> None:
        node = item.css_first("a")
        titles = node.text().strip().split("subtitle ")[-1].split("\n")
        _href = node.attributes["href"].split("/")  # type: ignore
        href = _href[-1]
        download_url = f"https://yifysubtitles.org/subtitle/{href}.zip"
        for subtitle_name in titles:
            self.prepare_subtitle(self.provider_name, subtitle_name, download_url, {})

    def skip_item(self, item: Node) -> bool:
        subtitle_language = item.css_first("span.sub-lang").child.text_content  # type: ignore
        subtitle_hi = item.css_matches("span.hi-subtitle")
        if subtitle_language.lower() != self.current_language.lower():  # type: ignore
            return True
        if not self.subtitle_hi_match(subtitle_hi):
            return True
        return False


class YifiSubtitles(YifySubtitlesScraper):
    def __init__(self, *args, **kwargs) -> None:
        YifySubtitlesScraper.__init__(self, *args, **kwargs)
        self.provider_name = self.__class__.__name__.lower()

    def start_search(self, *args, **kwargs) -> None:
        self.get_subtitles()
