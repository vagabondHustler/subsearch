from typing import Any

from curl_cffi import requests as curl_requests
from curl_cffi.requests import Response

from subsearch.providers import provider_helper
from subsearch.runtime.logging.logger import log
from subsearch.runtime.models.exceptions import (
    MissingApiKey,
    ProviderResponseUnrecognized,
)
from subsearch.runtime.models import ProviderDiagnosticStatus

API_BASE_URL = "https://api.subsource.net/api/v1"


class SubsourceApi:
    def __init__(self, api_key: str) -> None:
        self.api_key = api_key
        self.session = curl_requests.Session(impersonate="chrome", headers={"X-API-Key": api_key})

    def search_by_imdb(self, imdb_id: str, content_type: str) -> Response:
        return self.session.get(
            f"{API_BASE_URL}/movies/search",
            params={"searchType": "imdb", "imdb": imdb_id, "type": content_type},
        )

    def list_subtitles(self, movie_id: int, language: str) -> Response:
        return self.session.get(
            f"{API_BASE_URL}/subtitles",
            params={"movieId": movie_id, "language": language},
        )

    def download_url(self, subtitle_id: int) -> str:
        return f"{API_BASE_URL}/subtitles/{subtitle_id}/download"

    def auth_headers(self) -> dict[str, str]:
        return {"X-API-Key": self.api_key}

    def response_status_ok(self, response: Response) -> bool:
        log.debug(f"{response.url} status_code: {response.status_code} {response.reason}")
        return response.status_code == 200


class Subsource(provider_helper.ProviderHelper):
    def __init__(self, *args, **kwargs) -> None:
        provider_helper.ProviderHelper.__init__(self, *args, **kwargs)
        self.provider_name = self.__class__.__name__.lower()
        self.api_key = self.app_config.subsource_api_key

    def start_search(self, *args, **kwargs) -> None:
        if not self.api_key:
            log.warning(f"{self.provider_name} skipped: no API key configured. Add your Subsource API key in settings.")
            self.report_diagnostic_status(ProviderDiagnosticStatus.NO_RESPONSE, 0)
            raise MissingApiKey(self.provider_name)
        self.run_search(self._search_and_collect)

    def _search_and_collect(self) -> ProviderDiagnosticStatus:
        api = SubsourceApi(self.api_key)
        content_type = "series" if self.release_data.tvseries else "movie"
        search_response = api.search_by_imdb(self.release_data.imdb_id, content_type)
        if not api.response_status_ok(search_response):
            return ProviderDiagnosticStatus.NO_RESPONSE

        movie_id = self._matching_movie_id(search_response)
        if movie_id is None:
            return ProviderDiagnosticStatus.OK

        subtitles_response = api.list_subtitles(movie_id, self.app_config.selected_language)
        if not api.response_status_ok(subtitles_response):
            return ProviderDiagnosticStatus.NO_RESPONSE

        self._collect_subtitles(api, subtitles_response)
        return ProviderDiagnosticStatus.OK

    def _matching_movie_id(self, response: Response) -> int | None:
        data = response.json()
        if "data" not in data:
            raise ProviderResponseUnrecognized("movies/search response missing 'data'")
        for movie in data["data"]:
            if self._skip_movie(movie):
                continue
            return movie["movieId"]
        return None

    def _collect_subtitles(self, api: SubsourceApi, response: Response) -> None:
        data = response.json()
        if "data" not in data:
            raise ProviderResponseUnrecognized("subtitles response missing 'data'")
        for subtitle in data["data"]:
            reason = self._skip_reason(subtitle)
            if reason:
                name = ", ".join(subtitle.get("releaseInfo", []) or [str(subtitle.get("subtitleId", ""))])
                self.record_filtered_out(self.provider_name, name, reason)
                continue
            download_url = api.download_url(subtitle["subtitleId"])
            download_headers = api.auth_headers()
            for release_name in subtitle["releaseInfo"]:
                self.prepare_subtitle(
                    self.provider_name,
                    release_name,
                    download_url,
                    {},
                    download_headers=download_headers,
                )

    def _skip_movie(self, movie: dict[str, Any]) -> bool:
        keys = ["movieId", "type", "title"]
        if not self.keys_exist(movie, keys):
            return True
        if movie["title"].lower() != self.release_data.title:
            return True
        if self.release_data.tvseries and movie.get("season") != int(self.season_no_padding):
            return True
        return False

    def _skip_reason(self, subtitle: dict[str, Any]) -> str:
        keys = ["subtitleId", "releaseInfo", "language", "hearingImpaired"]
        if not self.keys_exist(subtitle, keys):
            return "malformed"
        if not self.subtitle_hi_match(subtitle["hearingImpaired"]):
            return "hi"
        if not self.subtitle_language_match(subtitle["language"]):
            return "language"
        return ""
