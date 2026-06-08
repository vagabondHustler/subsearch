import re
from typing import Any

from subsearch.runtime.logging.logger import log
from subsearch.runtime.models.model import ProviderDiagnosticStatus
from subsearch.io import http
from subsearch.providers import provider_helper
from subsearch.providers.provider_helper import combine_provider_diagnostic_status


class OpenSubtitlesScraper(provider_helper.ProviderHelper):
    def __init__(self, *args, **kwargs) -> None:
        provider_helper.ProviderHelper.__init__(self, *args, **kwargs)
        self.provider_name = ""

    def is_opensubtitles_down(self, tree: Any) -> bool:
        outage_text = self._outage_text(tree)
        if not outage_text:
            return False
        log.error(f"opensubtitles is down: {outage_text}")
        return True

    def _outage_text(self, tree: Any) -> str:
        if tree.css_matches("pre"):
            pre_text = tree.css_first("pre").text()
            if pre_text.startswith("Site will be online soon"):
                return pre_text
        body = tree.css_first("body")
        body_text = body.text() if body is not None else ""
        if "CANNOT CONNECT TO DB" in body_text or "problem with network connection to database" in body_text:
            return body_text.strip().splitlines()[0]
        return ""

    def classify_response(self, tree: Any) -> ProviderDiagnosticStatus:
        if self.is_opensubtitles_down(tree):
            return ProviderDiagnosticStatus.NO_RESPONSE
        if tree.css_first("channel") is None:
            return ProviderDiagnosticStatus.STRUCTURE_INVALID
        return ProviderDiagnosticStatus.OK

    def response_is_well_formed(self, tree: Any) -> bool:
        return self.classify_response(tree) is ProviderDiagnosticStatus.OK

    def get_subtitles(self, url: str) -> ProviderDiagnosticStatus:
        tree = http.request_parsed_response(url=url, timeout=self.request_timeout)
        if not tree:
            return ProviderDiagnosticStatus.NO_RESPONSE
        classification = self.classify_response(tree)
        if classification is not ProviderDiagnosticStatus.OK:
            return classification
        for item in tree.css("item"):
            enclosure = item.css_first("enclosure")
            if enclosure is None:
                continue
            download_url = enclosure.attributes["url"]
            if download_url is None:
                continue
            released_as = item.css_first("description").child.text_content.strip()  # type: ignore
            # matches the value in lines like "Also Known As: Some Title;" — captures between ": " and ";"
            subtitle_name = re.findall("^.*?: (.*?);", released_as)[0]
            self.prepare_subtitle(self.provider_name, subtitle_name, download_url, {})
        return ProviderDiagnosticStatus.OK

    def with_hash(self, url: str, subtitle_name: str) -> ProviderDiagnosticStatus:
        tree = http.request_parsed_response(url=url, timeout=self.request_timeout)
        if not tree:
            return ProviderDiagnosticStatus.NO_RESPONSE
        if self.is_opensubtitles_down(tree):
            return ProviderDiagnosticStatus.NO_RESPONSE
        bt_dwl_bt = tree.css_first("#bt-dwl-bt")
        if bt_dwl_bt is None:
            return ProviderDiagnosticStatus.OK
        sub_id = bt_dwl_bt.attributes["data-product-id"]
        download_url = f"https://dl.opensubtitles.org/en/download/sub/{sub_id}"
        self.prepare_subtitle(self.provider_name, subtitle_name, download_url, {}, percentage_override=100)
        return ProviderDiagnosticStatus.OK


class OpenSubtitles(OpenSubtitlesScraper):
    def __init__(self, *args, **kwargs) -> None:
        OpenSubtitlesScraper.__init__(self, *args, **kwargs)
        self.provider_name = self.__class__.__name__.lower()

    def _do_search(self) -> ProviderDiagnosticStatus:
        hash_health = self.with_hash(self.url_opensubtitles_hash[0], self.release)
        site_health = self.get_subtitles(self.url_opensubtitles[0])
        return combine_provider_diagnostic_status(hash_health, site_health)

    def start_search(self, *args, **kwargs) -> None:
        self.run_search(self._do_search)
