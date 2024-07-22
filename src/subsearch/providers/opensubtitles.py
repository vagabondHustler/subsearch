import re
from typing import Any

from subsearch.globals import log
from subsearch.providers import common_utils


class OpenSubtitlesScraper(common_utils.ProviderHelper):
    def __init__(self, *args, **kwargs) -> None:
        common_utils.ProviderHelper.__init__(self, *args, **kwargs)
        self.provider_name = ""

    def is_opensubtitles_down(self, tree: Any) -> bool:
        is_offline = tree.css_matches("pre")
        if is_offline is False:
            return False
        offline_text = tree.css_first("pre").text()
        if offline_text.startswith("Site will be online soon"):
            log.stdout(f"opensubtitles is down: {offline_text}", level="error")
            return True
        return False

    def get_subtitles(self, url: str) -> None:
        tree = common_utils.request_parsed_response(url=url, timeout=self.request_timeout)
        if not tree:
            return None
        items = tree.css("item")
        if self.is_opensubtitles_down(tree):
            return None
        for item in items:
            download_url = item.css_first("enclosure").attributes["url"]
            released_as = item.css_first("description").child.text_content.strip()  # type: ignore
            subtitle_name = re.findall("^.*?: (.*?);", released_as)[0]  # https://regex101.com/r/LWAmJK/1
            self.prepare_subtitle(self.provider_name, subtitle_name, download_url, {})

    def with_hash(self, url: str, subtitle_name: str):
        tree = common_utils.request_parsed_response(url=url, timeout=self.request_timeout)
        if not tree:
            return None
        if self.is_opensubtitles_down(tree):
            return None
        try:
            sub_id = tree.css_first("#bt-dwl-bt").attributes["data-product-id"]
        except AttributeError:
            return None
        download_url = f"https://dl.opensubtitles.org/en/download/sub/{sub_id}"
        self.prepare_subtitle(self.provider_name, subtitle_name, download_url)


class OpenSubtitles(OpenSubtitlesScraper):
    def __init__(self, *args, **kwargs) -> None:
        OpenSubtitlesScraper.__init__(self, *args, **kwargs)
        self.provider_name = self.__class__.__name__.lower()

    def start_search(self, flag: str) -> None:
        flags = {"hash": self.search_site, "site": self.search_hash}
        flags[flag]()

    def search_hash(self) -> None:
        self.with_hash(self.url_opensubtitles_hash, self.release)

    def search_site(self) -> None:
        self.get_subtitles(self.url_opensubtitles)
