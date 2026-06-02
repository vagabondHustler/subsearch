import re
from typing import Any

from subsearch.logger import log
from subsearch.io import http
from subsearch.providers import data_container


class OpenSubtitlesScraper(data_container.ProviderHelper):
    def __init__(self, *args, **kwargs) -> None:
        data_container.ProviderHelper.__init__(self, *args, **kwargs)
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
        tree = http.request_parsed_response(url=url, timeout=self.request_timeout)
        if not tree:
            return None
        items = tree.css("item")
        if self.is_opensubtitles_down(tree):
            return None
        for item in items:
            enclosure = item.css_first("enclosure")
            if enclosure is None:
                continue
            download_url = enclosure.attributes["url"]
            if download_url is None:
                continue
            released_as = item.css_first("description").child.text_content.strip()  # type: ignore
            subtitle_name = re.findall("^.*?: (.*?);", released_as)[0]  # https://regex101.com/r/LWAmJK/1
            self.prepare_subtitle(self.provider_name, subtitle_name, download_url, {})

    def with_hash(self, url: str, subtitle_name: str) -> None:
        tree = http.request_parsed_response(url=url, timeout=self.request_timeout)
        if not tree:
            return None
        if self.is_opensubtitles_down(tree):
            return None
        bt_dwl_bt = tree.css_first("#bt-dwl-bt")
        if bt_dwl_bt is None:
            return None
        sub_id = bt_dwl_bt.attributes["data-product-id"]
        download_url = f"https://dl.opensubtitles.org/en/download/sub/{sub_id}"
        self.prepare_subtitle(self.provider_name, subtitle_name, download_url, {})


class OpenSubtitles(OpenSubtitlesScraper):
    def __init__(self, *args, **kwargs) -> None:
        OpenSubtitlesScraper.__init__(self, *args, **kwargs)
        self.provider_name = self.__class__.__name__.lower()

    def start_search(self, *args, **kwargs) -> None:
        self.with_hash(self.url_opensubtitles_hash, self.release)
        self.get_subtitles(self.url_opensubtitles)
