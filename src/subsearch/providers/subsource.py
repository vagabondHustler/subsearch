from typing import Any, Iterable

import cloudscraper
import requests

from subsearch.globals import log
from subsearch.globals.dataclasses import Subtitle
from subsearch.providers import common_utils
from subsearch.utils import string_parser


class SubsourcePost:
    def __init__(self, **kwargs) -> None:
        base_url = "https://api.subsource.net/api"
        self.api = {
            "search_movie": f"{base_url}/searchMovie",
            "get_movie": f"{base_url}/getMovie",
            "get_sub": f"{base_url}/getSub",
        }

        self.post = cloudscraper.requests.post

    def search_movie(self, imdb_id: str, *args, **kwargs) -> requests.Response:
        response = self.post(url=self.api["search_movie"], data={"query": imdb_id})
        return response

    def get_movie(self, lang: str, movie_name: str, *args, **kwargs) -> requests.Response:
        response = self.post(url=self.api["get_movie"], data={"langs": [lang], "movieName": movie_name})
        return response

    def get_sub(self, movie: str, lang: str, id: str, *args, **kwargs) -> requests.Response:
        response = self.post(url=self.api["get_sub"], data={"movie": movie, "lang": lang, "id": id})
        return response


class SubsourceScraper(common_utils.ProviderHelper):
    def __init__(self, **kwargs) -> None:
        common_utils.ProviderHelper.__init__(self, **kwargs)
        self.post_request = SubsourcePost()

    def parse_search_movie_response(self, response: requests.Response) -> str:
        data = response.json()
        found_items = data["found"]
        if len(found_items) == 0:
            return ""
        for release in found_items:
            if not self.continue_search_movie(release):
                continue
            return release["linkName"]

        return ""

    def parse_get_movie_response(self, response: requests.Response) -> list[dict[str, str]]:
        data = response.json()
        subtitle_data = []
        filtered = {}

        for sub in data["subs"]:
            if self.continue_get_movie(sub):
                continue

            post_data = self.set_post_data(sub)
            release_name = sub["releaseName"]
            pct_result = string_parser.calculate_match(release_name, self.release)

            if self.release_in_post_data(release_name, subtitle_data):
                filtered[pct_result] = post_data
                continue
            if pct_result <= self.percentage_threashold:
                filtered[pct_result] = post_data
                continue

            subtitle_data.append(post_data)

        sorted_dict = dict(sorted(filtered.items(), key=lambda item: item[0], reverse=True))
        for k, v in list(sorted_dict.items()):
            if len(subtitle_data) == 4:
                break
            v = sorted_dict.pop(k)
            subtitle_data.append(v)
        return subtitle_data

    def set_post_data(self, sub: dict[str, Any]):
        data = {
            "movie": sub["linkName"],
            "lang": sub["lang"],
            "id": str(sub["subId"]),
            "release_name": sub["releaseName"],
        }
        return data

    def release_in_post_data(self, release_name: str, subtitle_data: list[dict[str, Any]]) -> bool:
        for i in subtitle_data:
            if release_name in i.values():
                return True
        return False

    def parse_get_sub_response(self, response: requests.Response) -> dict[str, str]:
        data = response.json()
        sub = data["sub"]

        if self.continue_get_sub(sub):
            return {"": ""}

        download_token = sub["downloadToken"]
        download_url = f"https://api.subsource.net/api/downloadSub/{download_token}"
        return download_url

    def continue_search_movie(self, items: dict[str, Any]) -> bool:
        keys = ["subCount", "releaseYear", "type", "title", "linkName"]
        if not self._keys_exsist(items, keys):
            return True
        if items["subCount"] == 0:
            return True
        elif self.year != items["releaseYear"] or self.year - 1 != items["releaseYear"]:
            return True
        elif self.tvseries and items["type"] == "Movie":
            return True
        elif not self.tvseries and items["type"] == "TVSeries":
            return True
        elif items["title"].lower() != self.title:
            return True
        return False

    def continue_get_movie(self, items: dict[str, Any]) -> bool:
        keys = ["releaseName", "linkName", "lang", "subId"]
        if not self._keys_exsist(items, keys):
            return True
        elif not self._subtitle_hi_match(items):
            return True
        elif not self._subtitle_language_match(items):
            return True
        return False

    def continue_get_sub(self, items: dict[str, Any]) -> bool:
        keys = ["ri", "downloadToken"]
        if not self._keys_exsist(items, keys):
            return True
        return False

    def _subtitle_hi_match(self, data: dict[str, Any]) -> bool:
        if self.hi_sub and self.non_hi_sub:
            pass
        else:
            if not self.hi_sub and data["hi"] == 1:
                return False
            if not self.non_hi_sub and data["hi"] == 0:
                return False
        return True

    def _subtitle_language_match(self, data: dict[str, Any]) -> bool:
        if self.current_language.lower() != data["lang"].lower():
            return False
        return True

    def _keys_exsist(self, data: dict[str, Any], keys: list[str]) -> bool:
        for key in keys:
            if key not in data:
                return False
        return True


class Subsource(SubsourceScraper):
    def __init__(self, **kwargs) -> None:
        SubsourceScraper.__init__(self, **kwargs)
        self.provider_name = self.__class__.__name__.lower()

    def start_search(self, **kwargs) -> list[Subtitle] | None:
        search_results = self.handle_search_movie(self.url_subsource)

        if not search_results:
            return []

        movie_results = self.handle_get_movie(search_results)

        if not movie_results:
            return []

        subtitle_data = self.handle_get_sub(movie_results)

        if not subtitle_data:
            return []

        self._process_subtitle_data(self.provider_name, subtitle_data)

    def response_status_ok(self, response: requests.Response, msg: str = "") -> bool:
        api = response.url.split("/")[-1]
        status = f"POST: {api}, status code: {response.status_code}, reason: {response.reason}"
        if msg:
            log.log(f"{msg}, {status}")
        else:
            log.log(f"{self.provider_name}, {status}")
        if response.status_code != 200:
            return False
        return True

    def handle_search_movie(self, imdb_id: str) -> str:
        response = self.post_request.search_movie(imdb_id)
        if not self.response_status_ok(response):
            return ""
        data = self.parse_search_movie_response(response)
        return data

    def handle_get_movie(self, parsed_search_movie_data) -> list[dict[str, str]]:
        response = self.post_request.get_movie(self.current_language, parsed_search_movie_data)
        if not self.response_status_ok(response):
            return [{"": ""}]
        data = self.parse_get_movie_response(response)
        return data

    def handle_get_sub(self, parsed_get_movie_data) -> dict[str, str]:
        subtitles: dict[str, str] = {}
        for subtitle in parsed_get_movie_data:
            response = self.post_request.get_sub(subtitle["movie"], subtitle["lang"], subtitle["id"])
            if not self.response_status_ok(response, subtitle["release_name"]):
                return [{"": ""}]
            download_url = self.parse_get_sub_response(response)
            subtitles[subtitle["release_name"]] = download_url
        return subtitles

    @property
    def accepted_subtitles(self) -> list[Subtitle]:
        return self._accepted_subtitles

    @property
    def rejected_subtitles(self) -> list[Subtitle]:
        return self._rejected_subtitles
