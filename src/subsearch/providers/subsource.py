from typing import Any

import cloudscraper
import requests

from subsearch.globals import log
from subsearch.globals.dataclasses import Subtitle
from subsearch.providers import common_utils


class SubsourceApi:
    def __init__(self, *args, **kwargs) -> None:
        self.method = {
            "search_movie": f"https://api.subsource.net/api/searchMovie",
            "get_movie": f"https://api.subsource.net/api/getMovie",
            "get_sub": f"https://api.subsource.net/api/getSub",
            "download_sub": f"https://api.subsource.net/api/downloadSub",
        }

        self.post = cloudscraper.requests.post
        self.call_limit = 5
        self.provider_name = ""

    def search_movie(self, imdb_id: str, *args, **kwargs) -> requests.Response:
        url = self.method["search_movie"]
        data = {"query": imdb_id}
        response = self.post(url=url, data=data)
        return response

    def get_movie(self, lang: str, movie_name: str, *args, **kwargs) -> requests.Response:
        url = self.method["get_movie"]
        data = {"langs": [lang], "movieName": movie_name}
        response = self.post(url=url, data=data)
        return response

    def get_tvseries(self, lang: str, movie_name: str, season: str, *args, **kwargs) -> requests.Response:
        url = self.method["get_movie"]
        data = {"langs": [lang], "movieName": movie_name, "season": season}
        response = self.post(url=url, data=data)
        return response

    def get_sub(self, movie: str, lang: str, id: str, *args, **kwargs) -> requests.Response:
        url = self.method["get_sub"]
        data = {"movie": movie, "lang": lang, "id": id}
        response = self.post(url=url, data=data)
        return response

    def response_status_ok(self, response: requests.Response) -> bool:
        log.stdout(f"{response.url} status_code: {response.status_code} {response.reason}")
        if response.status_code != 200:
            return False
        return True


class SubsourceParser(common_utils.ProviderHelper):
    def __init__(self, *args, **kwargs) -> None:
        common_utils.ProviderHelper.__init__(self, *args, **kwargs)
        self.api = SubsourceApi()
        self.provider_name = ""
        self.api.provider_name = self.provider_name

    def parse_search_movie_response(self, response: requests.Response) -> dict[str, Any]:
        data = response.json()
        found_items = data["found"]
        parsed_response = {}
        if len(found_items) == 0:
            return {}
        for release in found_items:
            if self.skip_search_movie_item(release):
                continue
            if self.tvseries:
                season = f"season-{self.season_no_padding}"
                parsed_response["season"] = season
            parsed_response["link_name"] = release["linkName"]
        return parsed_response

    def parse_get_movie_response(self, response: requests.Response) -> None:
        data = response.json()
        for sub in data["subs"]:
            if self.skip_get_movie_item(sub):
                continue
            request_data = self.set_post_data(sub)
            subtitle_name = sub["releaseName"]
            if self.skip_tvseries(subtitle_name):
                continue
            self.prepare_subtitle(self.provider_name, subtitle_name, "", request_data=request_data)

    def skip_tvseries(self, subtitle_name: str) -> bool:
        if self.tvseries:
            patterns = self.ok_season_episode_pattern
            return any(item in subtitle_name.lower() for item in patterns)
        return False

    def set_post_data(self, x: dict[str, Any]) -> dict[str, Any]:
        data = {
            "movie": x["linkName"],
            "lang": x["lang"],
            "id": str(x["subId"]),
            "release_name": x["releaseName"],
            "api_method": self.api.method["get_sub"],
        }
        return data

    def release_in_post_data(self, release_name: str, subtitle_data: list[dict[str, Any]]) -> bool:
        for i in subtitle_data:
            if release_name in i.values():
                return True
        return False

    def parse_get_sub_response(self, response: requests.Response) -> str:
        data = response.json()
        sub = data["sub"]

        if self.skip_get_sub_item(sub):
            return ""

        return f"{self.api.method["download_sub"]}/{sub["downloadToken"]}"

    def skip_search_movie_item(self, items: dict[str, Any]) -> bool:
        keys = ["subCount", "type", "title", "linkName"]
        if not self.keys_exsist(items, keys):
            return True
        if items["subCount"] == 0:
            return True
        elif self.tvseries and items["type"] == "Movie":
            return True
        elif not self.tvseries and items["type"] == "TVSeries":
            return True
        elif items["title"].lower() != self.title:
            return True
        return False

    def skip_get_movie_item(self, items: dict[str, Any]) -> bool:
        keys = ["releaseName", "linkName", "lang", "subId"]
        if not self.keys_exsist(items, keys):
            return True
        elif not self.subtitle_hi_match(items["hi"]):
            return True
        elif not self.subtitle_language_match(items["lang"]):
            return True
        return False

    def skip_get_sub_item(self, items: dict[str, Any]) -> bool:
        keys = ["ri", "downloadToken"]
        if not self.keys_exsist(items, keys):
            return True
        return False


class Subsource(SubsourceParser):
    def __init__(self, *args, **kwargs) -> None:
        SubsourceParser.__init__(self, *args, **kwargs)
        self.provider_name = self.__class__.__name__.lower()

    def start_search(self, *args, **kwargs) -> None:
        self.api.call_limit = 5  # default, requests made in quick succession
        release_results = self.find_release(self.imdb_id)
        self.find_subtitles(release_results)

    def find_release(self, imdb_id: str) -> dict[str, str]:
        response = self.api.search_movie(imdb_id)
        if not self.api.response_status_ok(response):
            return ""
        data = self.parse_search_movie_response(response)
        return data

    def find_subtitles(self, request_data: dict[str, str]) -> None:
        if not request_data:
            return None

        if self.tvseries:
            response = self.api.get_tvseries(self.current_language, request_data["link_name"], request_data["season"])
        else:
            response = self.api.get_movie(self.current_language, request_data["link_name"])

        if not self.api.response_status_ok(response):
            return None

        self.parse_get_movie_response(response)


class GetDownloadUrl:
    def __init__(self) -> None:
        self._api = SubsourceApi()
        self._response = None

    def get_url(self, item: Subtitle) -> str:
        self._response = self._api.get_sub(
            item.request_data["movie"], item.request_data["lang"], item.request_data["id"]
        )
        if self._api.response_status_ok(self._response):
            return self._parse_get_sub_response()
        return ""

    def _parse_get_sub_response(self) -> str:
        data = self._response.json()
        sub = data["sub"]

        if self._skip_get_sub_item(sub):
            return ""

        return f"{self._api.method["download_sub"]}/{sub["downloadToken"]}"

    def _skip_get_sub_item(self, items: dict[str, Any]) -> bool:
        keys = ["ri", "downloadToken"]
        if not self._keys_exsist(items, keys):
            return True
        return False

    def _keys_exsist(self, dict_: dict[str, Any], keys: list[str]) -> bool:
        for key in keys:
            if key not in dict_:
                return False
        return True
