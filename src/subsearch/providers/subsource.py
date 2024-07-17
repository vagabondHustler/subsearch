from typing import Any, Iterable

import cloudscraper
import requests

from subsearch.globals import log
from subsearch.globals.dataclasses import Subtitle
from subsearch.providers import common_utils
from subsearch.utils import string_parser

# TODO refactor this mess ^_^


class SubsourceApi:
    def __init__(self, base_url: str, **kwargs) -> None:
        self.method = {
            "search_movie": f"{base_url}/searchMovie",
            "get_movie": f"{base_url}/getMovie",
            "get_sub": f"{base_url}/getSub",
        }

        self.post = cloudscraper.requests.post

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
        status = f"Url: {response.url}, status code: {response.status_code}, reason: {response.reason}"
        log.stdout(f"{status}", print_allowed=False)
        if response.status_code != 200:
            return False
        return True


class SubsourceParser(common_utils.ProviderHelper):
    def __init__(self, **kwargs) -> None:
        common_utils.ProviderHelper.__init__(self, **kwargs)
        self.api = SubsourceApi(self.url_subsource)

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

    def parse_get_movie_response(self, response: requests.Response) -> list[dict[str, str]]:
        data = response.json()
        all_subtitles = {}

        for sub in data["subs"]:
            if self.skip_get_movie_item(sub):
                continue
            post_data = self.set_post_data(sub)
            release_name = sub["releaseName"]
            if self.skip_tvseries(release_name):
                continue
            pct_result = string_parser.calculate_match(release_name, self.release)
            all_subtitles[pct_result] = post_data

        sorted_data = self.populate_return_data(all_subtitles, limit=5)
        return sorted_data

    def populate_return_data(self, all_subtitles: list[dict], limit: int) -> list[dict[str, str]]:
        subtitle_data = []
        sorted_dict = dict(sorted(all_subtitles.items(), key=lambda item: item[0], reverse=True))
        for k, v in list(sorted_dict.items()):
            if len(subtitle_data) == limit:
                break
            v = sorted_dict.pop(k)
            subtitle_data.append(v)
        return subtitle_data

    def skip_tvseries(self, release_name: str):
        if self.tvseries:
            patterns = self.ok_season_episode_pattern
            return any(item in release_name.lower() for item in patterns)
        return False

    def set_post_data(self, sub: dict[str, Any]):  # -> dict[str, Any]:
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

        if self.skip_get_sub_item(sub):
            return {}

        download_token = sub["downloadToken"]
        download_url = f"https://api.subsource.net/api/downloadSub/{download_token}"
        return download_url

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
        elif not self.subtitle_hi_match(items):
            return True
        elif not self.subtitle_language_match(items):
            return True
        return False

    def skip_get_sub_item(self, items: dict[str, Any]) -> bool:
        keys = ["ri", "downloadToken"]
        if not self.keys_exsist(items, keys):
            return True
        return False


class Subsource(SubsourceParser):
    def __init__(self, **kwargs) -> None:
        SubsourceParser.__init__(self, **kwargs)
        self.provider_name = self.__class__.__name__.lower()

    def start_search(self, **kwargs) -> None:
        search_results = self.handle_search_movie(self.imdb_id)

        if not search_results:
            return None

        movie_results = self.handle_get_movie(search_results)

        if not movie_results:
            return None

        subtitle_data = self.handle_get_sub(movie_results)

        if not subtitle_data:
            return None

        self._process_subtitle_data(self.provider_name, subtitle_data)

    def handle_search_movie(self, imdb_id: str) -> dict[str, str]:
        response = self.api.search_movie(imdb_id)
        if not self.api.response_status_ok(response):
            return ""
        data = self.parse_search_movie_response(response)
        return data

    def handle_get_movie(self, request_data) -> dict[str, str]:
        if self.tvseries:
            response = self.api.get_tvseries(
                self.current_language,
                request_data["link_name"],
                request_data["season"],
            )
        else:
            response = self.api.get_movie(self.current_language, request_data["link_name"])
        if not self.api.response_status_ok(response):
            return {}
        data = self.parse_get_movie_response(response)
        return data

    def handle_get_sub(self, parsed_get_movie_data) -> dict[str, str]:
        subtitles: dict[str, str] = {}
        for subtitle in parsed_get_movie_data:
            response = self.api.get_sub(subtitle["movie"], subtitle["lang"], subtitle["id"])
            if not self.api.response_status_ok(response):
                return {}
            download_url = self.parse_get_sub_response(response)
            subtitles[subtitle["release_name"]] = download_url
        return subtitles

    @property
    def accepted_subtitles(self) -> list[Subtitle]:
        return self._accepted_subtitles

    @property
    def rejected_subtitles(self) -> list[Subtitle]:
        return self._rejected_subtitles
