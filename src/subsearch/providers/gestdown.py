from typing import Any
from urllib.parse import quote

from curl_cffi import requests as curl_requests
from curl_cffi.requests import Response

from subsearch.parsing.gestdown_names import normalize_show_name
from subsearch.providers import provider_helper
from subsearch.runtime.logging.events import LogEvent
from subsearch.runtime.logging.logger import log
from subsearch.runtime.models import ProviderDiagnosticStatus
from subsearch.runtime.models.exceptions import ProviderResponseUnrecognized

API_BASE_URL = "https://api.gestdown.info"


class GestdownApi:
    def __init__(self) -> None:
        self.session = curl_requests.Session(impersonate="chrome", headers={"accept": "application/json"})

    def search_show(self, title: str) -> Response:
        return self.session.get(f"{API_BASE_URL}/shows/search/{quote(title)}")

    def list_subtitles(self, show_id: str, season: str, episode: str, language_name: str) -> Response:
        return self.session.get(f"{API_BASE_URL}/subtitles/get/{show_id}/{season}/{episode}/{language_name}")

    def season_packs(self, show_id: str, season: str, language_name: str) -> Response:
        # Season packs bundle a whole season into one archive. Not consumed yet; the endpoint and
        # its "seasonPacks" response key are kept here so a future feature can offer them as a
        # fallback when no per-episode subtitle clears the threshold.
        return self.session.get(f"{API_BASE_URL}/shows/{show_id}/{season}/{language_name}/season-packs")

    def download_url(self, download_uri: str) -> str:
        return f"{API_BASE_URL}{download_uri}"

    def response_status_ok(self, response: Response) -> bool:
        log.event(
            LogEvent.PROVIDER_GESTDOWN_STATUS,
            level="debug",
            url=response.url,
            status_code=response.status_code,
            reason=response.reason,
        )
        return response.status_code == 200


class Gestdown(provider_helper.ProviderHelper):
    def __init__(self, *args, **kwargs) -> None:
        provider_helper.ProviderHelper.__init__(self, *args, **kwargs)
        self.provider_name = self.__class__.__name__.lower()

    def start_search(self, *args, **kwargs) -> None:
        self.run_search(self._search_and_collect)

    def _search_and_collect(self) -> ProviderDiagnosticStatus:
        if not self.release_data.tvseries:
            return ProviderDiagnosticStatus.OK

        api = GestdownApi()
        search_response = api.search_show(self.release_data.title)
        if not api.response_status_ok(search_response):
            return ProviderDiagnosticStatus.NO_RESPONSE

        show_id = self._matching_show_id(search_response)
        if show_id is None:
            return ProviderDiagnosticStatus.OK

        subtitles_response = api.list_subtitles(
            show_id, self.season_no_padding, self.episode_no_padding, self._language_name
        )
        if not api.response_status_ok(subtitles_response):
            return ProviderDiagnosticStatus.NO_RESPONSE

        self._collect_subtitles(api, subtitles_response)
        return ProviderDiagnosticStatus.OK

    @property
    def _language_name(self) -> str:
        return self.language_data[self.app_config.selected_language]["name"]  # type: ignore[index]

    def _matching_show_id(self, response: Response) -> str | None:
        data = response.json()
        if "shows" not in data:
            raise ProviderResponseUnrecognized("shows/search response missing 'shows'")
        target = normalize_show_name(self.release_data.title)
        show = self._select_show(data["shows"], target)
        if show is None:
            return None
        log.event(LogEvent.PROVIDER_SEARCHING, level="debug", provider=self.provider_name)
        return show["id"]

    def _select_show(self, shows: list[dict[str, Any]], target: str) -> dict[str, Any] | None:
        exact = [show for show in shows if normalize_show_name(show["name"]) == target]
        chosen = self._prefer_by_season(exact)
        if chosen is not None:
            return chosen
        startswith = [show for show in shows if normalize_show_name(show["name"]).startswith(target)]
        return self._prefer_by_season(startswith, require_season=True)

    def _prefer_by_season(
        self, candidates: list[dict[str, Any]], require_season: bool = False
    ) -> dict[str, Any] | None:
        if not candidates:
            return None
        season = int(self.season_no_padding)
        with_season = [show for show in candidates if season in show.get("seasons", [])]
        if with_season:
            return max(with_season, key=lambda show: show.get("nbSeasons", 0))
        if require_season:
            return None
        return max(candidates, key=lambda show: show.get("nbSeasons", 0))

    def _collect_subtitles(self, api: GestdownApi, response: Response) -> None:
        data = response.json()
        if "matchingSubtitles" not in data:
            raise ProviderResponseUnrecognized("subtitles response missing 'matchingSubtitles'")
        for subtitle in data["matchingSubtitles"]:
            reason = self._skip_reason(subtitle)
            release_name = self._release_name(subtitle)
            if reason:
                self.record_filtered_out(self.provider_name, release_name, reason)
                continue
            download_url = api.download_url(subtitle["downloadUri"])
            self.prepare_subtitle(self.provider_name, release_name, download_url, {}, download_count=subtitle.get("downloadCount", 0))

    def _release_name(self, subtitle: dict[str, Any]) -> str:
        version = subtitle.get("version") or str(subtitle.get("subtitleId", ""))
        return f"{self.release_data.release} {version}".strip()

    def _skip_reason(self, subtitle: dict[str, Any]) -> str:
        keys = ["downloadUri", "version", "language", "hearingImpaired"]
        if not self.keys_exist(subtitle, keys):
            return "malformed"
        if not self.subtitle_hi_match(subtitle["hearingImpaired"]):
            return "hi"
        if not self.subtitle_language_match(subtitle["language"]):
            return "language"
        return ""
