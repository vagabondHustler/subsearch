import re
from typing import Any
from urllib.parse import quote

from selectolax.lexbor import LexborHTMLParser, LexborNode

from subsearch.io import http
from subsearch.providers import provider_helper
from subsearch.runtime.models import ProviderDiagnosticStatus
from subsearch.runtime.recorder import LogLevel, capture

DOMAIN = "https://www.tvsubtitles.net"

# matches a show page href like "tvshow-133.html" on the search results page, capturing the show id
_SHOW_HREF_PATTERN = re.compile(r"tvshow-(\d+)\.html")
# matches an episode page href like "episode-2077.html", capturing the episode id
_EPISODE_HREF_PATTERN = re.compile(r"episode-(\d+)\.html")
# matches a subtitle page href like "subtitle-3640.html", capturing the subtitle id
_SUBTITLE_HREF_PATTERN = re.compile(r"subtitle-(\d+)\.html")
# matches an episode label like "1x01" at the start of a cell, capturing season and episode numbers
_EPISODE_LABEL_PATTERN = re.compile(r"(\d{1,2})x(\d{1,4})")
# matches a trailing year range like " (2008-2013)" or " (2015)" on a show title, to strip it off
_YEAR_SUFFIX_PATTERN = re.compile(r"\s*\(\d{4}(?:-\d{4})?\)\s*$")
# matches JS string-fragment vars like: var s1= 'files/B'; — capturing the fragment value
_JS_FRAGMENT_PATTERN = re.compile(r"var\s+s\d+\s*=\s*'([^']*)'")


def _resolve_download_url(download_page_url: str, referer: str, timeout: tuple[int, int]) -> str | None:
    session = http.get_session()
    try:
        response = session.get(download_page_url, headers={"Referer": referer}, timeout=timeout)
    except Exception:
        return None
    if not 200 <= response.status_code < 300:
        return None
    fragments = _JS_FRAGMENT_PATTERN.findall(response.text)
    if not fragments:
        return None
    relative_path = "".join(fragments)
    return f"{DOMAIN}/{quote(relative_path, safe='/')}"


class TvSubtitlesScraper(provider_helper.ProviderHelper):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        provider_helper.ProviderHelper.__init__(self, *args, **kwargs)
        self.provider_name = ""

    def get_subtitles(self) -> ProviderDiagnosticStatus:
        if not self.release_data.tvseries:
            return ProviderDiagnosticStatus.OK
        show_tree = self._search_show()
        if show_tree is None:
            return ProviderDiagnosticStatus.NO_RESPONSE
        show_id = self._matching_show_id(show_tree)
        if show_id is None:
            return ProviderDiagnosticStatus.OK

        season_tree = http.request_parsed_response(
            url=f"{DOMAIN}/tvshow-{show_id}-{self.season_no_padding}.html", timeout=self.request_timeout
        )
        if season_tree is None:
            return ProviderDiagnosticStatus.NO_RESPONSE
        if not self.response_is_well_formed(season_tree):
            return ProviderDiagnosticStatus.STRUCTURE_INVALID
        episode_id = self._matching_episode_id(season_tree)
        if episode_id is None:
            return ProviderDiagnosticStatus.OK

        episode_tree = http.request_parsed_response(
            url=f"{DOMAIN}/episode-{episode_id}-{self.language_code}.html", timeout=self.request_timeout
        )
        if episode_tree is None:
            return ProviderDiagnosticStatus.NO_RESPONSE
        self._collect_subtitles(episode_tree)
        return ProviderDiagnosticStatus.OK

    @property
    def language_code(self) -> str:
        language = self.language_data[self.app_config.selected_language]  # type: ignore[index]
        return str(language.get("tvsubtitles_code") or language["two_letter_code"])

    def response_is_well_formed(self, tree: LexborHTMLParser) -> bool:
        return tree.css_first("table") is not None

    def _search_show(self) -> LexborHTMLParser | None:
        capture(f"{self.provider_name}: searching", level=LogLevel.DEBUG)
        return http.request_parsed_post(
            url=f"{DOMAIN}/search1.php", data={"qs": self.release_data.title}, timeout=self.request_timeout
        )

    def _matching_show_id(self, tree: LexborHTMLParser) -> str | None:
        for node in tree.css("a"):
            href = node.attributes.get("href") or ""
            match = _SHOW_HREF_PATTERN.search(href)
            if match and self._show_title(node) == self.release_data.title:
                return match.group(1)
        return None

    def _show_title(self, node: LexborNode) -> str:
        return _YEAR_SUFFIX_PATTERN.sub("", node.text().strip()).lower()

    def _matching_episode_id(self, tree: LexborHTMLParser) -> str | None:
        for row in tree.css("tr"):
            episode_link = self._episode_link_in_row(row)
            if episode_link is None:
                continue
            match = _EPISODE_HREF_PATTERN.search(episode_link.attributes.get("href") or "")
            if match:
                return match.group(1)
        return None

    def _episode_link_in_row(self, row: LexborNode) -> LexborNode | None:
        label_match = _EPISODE_LABEL_PATTERN.search(row.text())
        if not label_match:
            return None
        if int(label_match.group(1)) != int(self.season_no_padding):
            return None
        if int(label_match.group(2)) != int(self.episode_no_padding):
            return None
        for node in row.css("a"):
            if _EPISODE_HREF_PATTERN.search(node.attributes.get("href") or ""):
                return node
        return None

    def _collect_subtitles(self, tree: LexborHTMLParser) -> None:
        for node in tree.css("a"):
            match = _SUBTITLE_HREF_PATTERN.search(node.attributes.get("href") or "")
            if not match:
                continue
            release_name = self._subtitle_release_name(node)
            if not release_name:
                continue
            self._prepare_subtitle(match.group(1), release_name)

    def _subtitle_release_name(self, node: LexborNode) -> str:
        heading = node.css_first("div.subtitlen h5")
        return heading.text().strip() if heading is not None else ""

    def _prepare_subtitle(self, subtitle_id: str, release_name: str) -> None:
        download_page_url = f"{DOMAIN}/download-{subtitle_id}.html"
        referer = f"{DOMAIN}/subtitle-{subtitle_id}.html"
        download_url = _resolve_download_url(download_page_url, referer, self.request_timeout)
        if download_url is None:
            return
        self.prepare_subtitle(self.provider_name, release_name, download_url, {})


class TvSubtitles(TvSubtitlesScraper):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        TvSubtitlesScraper.__init__(self, *args, **kwargs)
        self.provider_name = self.__class__.__name__.lower()

    def start_search(self, *args: Any, **kwargs: Any) -> None:
        self.run_search(self.get_subtitles)
