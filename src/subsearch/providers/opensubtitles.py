import re
from typing import Any

from subsearch.globals.dataclasses import Subtitle
from subsearch.providers import common_utils
from subsearch.utils import io_log


class OpenSubtitlesScraper(common_utils.ProviderHelper):
    def __init__(self, **kwargs) -> None:
        common_utils.ProviderHelper.__init__(self, **kwargs)

    def is_opensubtitles_down(self, tree: Any) -> bool:
        is_offline = tree.css_matches("pre")
        if is_offline is False:
            return False
        offline_text = tree.css_first("pre").text()
        if offline_text.startswith("Site will be online soon"):
            io_log.stdout(f"opensubtitles is down: {offline_text}", level="error")
            return True
        return False

    def get_subtitles(self, url: str) -> dict[str, str]:
        subtitles: dict[str, str] = {}
        tree = common_utils.get_html_parser(url)
        items = tree.css("item")
        if self.is_opensubtitles_down(tree):
            return subtitles
        for item in items:
            dl_url = item.css_first("enclosure").attributes["url"]
            released_as = item.css_first("description").child.text_content.strip()  # type: ignore
            release_name = re.findall("^.*?: (.*?);", released_as)[0]  # https://regex101.com/r/LWAmJK/1
            subtitles[release_name] = dl_url  # type: ignore
        return subtitles

    def with_hash(self, url: str, release: str) -> dict[str, str]:
        subtitles: dict[str, str] = {}
        tree = common_utils.get_html_parser(url)
        if self.is_opensubtitles_down(tree):
            return subtitles
        try:
            sub_id = tree.css_first("#bt-dwl-bt").attributes["data-product-id"]
        except AttributeError:
            return subtitles
        subtitles[release] = f"https://dl.opensubtitles.org/en/download/sub/{sub_id}"
        return subtitles


class OpenSubtitles(OpenSubtitlesScraper):
    def __init__(self, **kwargs) -> None:
        OpenSubtitlesScraper.__init__(self, **kwargs)
        self.provider_name = self.__class__.__name__.lower()

    def start_search(self, flag: str) -> None:
        flags = {"hash": self.search_site, "site": self.search_hash}
        flags[flag]()

    def search_hash(self) -> None:
        subtitle_data = self.with_hash(self.url_opensubtitles_hash, self.release)

        if not subtitle_data:
            return None

        io_log.stdout_match(
            provider=self.provider_name,
            subtitle_name=self.release,
            result=100,
            threshold=self.app_config.accept_threshold,
        )
        self._process_subtitle_data(self.provider_name, subtitle_data)

    def search_site(self) -> None:
        subtitle_data = self.get_subtitles(self.url_opensubtitles)

        if not subtitle_data:
            return None

        self._process_subtitle_data(self.provider_name, subtitle_data)

    @property
    def accepted_subtitles(self) -> list[Subtitle]:
        return self._accepted_subtitles

    @property
    def rejected_subtitles(self) -> list[Subtitle]:
        return self._rejected_subtitles
