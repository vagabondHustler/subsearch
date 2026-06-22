from typing import Any
from urllib.parse import quote

from curl_cffi import requests as curl_requests

from subsearch.parsing.gestdown_names import normalize_show_name
from subsearch.parsing.imdb_lookup import EpisodeSuggestion, SeasonSuggestion
from subsearch.runtime.logging.events import LogEvent
from subsearch.runtime.logging.logger import log

API_BASE_URL = "https://api.gestdown.info"


class GestdownLookup:
    def __init__(self) -> None:
        self.session = curl_requests.Session(impersonate="chrome", headers={"accept": "application/json"})

    def find_season_suggestions(self, title: str) -> list[SeasonSuggestion]:
        show = self._matching_show(title)
        if show is None:
            log.event(LogEvent.GESTDOWN_SEASONS_FAILED, level="warning", title=title)
            return []
        suggestions = [SeasonSuggestion(number=season) for season in sorted(show.get("seasons", []))]
        log.event(LogEvent.GESTDOWN_SEASONS, title=title, seasons=len(suggestions))
        return suggestions

    def find_episode_suggestions(self, title: str, season: int, language_name: str) -> list[EpisodeSuggestion]:
        show = self._matching_show(title)
        if show is None:
            log.event(LogEvent.GESTDOWN_EPISODES_FAILED, level="warning", title=title, season=season)
            return []
        response = self.session.get(f"{API_BASE_URL}/shows/{show['id']}/{season}/{quote(language_name)}")
        if response.status_code != 200:
            log.event(LogEvent.GESTDOWN_EPISODES_FAILED, level="warning", title=title, season=season)
            return []
        suggestions = [
            EpisodeSuggestion(season=season, number=episode["number"], title=episode.get("title") or "")
            for episode in response.json().get("episodes", [])
            if episode.get("number")
        ]
        log.event(LogEvent.GESTDOWN_EPISODES, title=title, season=season, episodes=len(suggestions))
        return suggestions

    def _matching_show(self, title: str) -> dict[str, Any] | None:
        response = self.session.get(f"{API_BASE_URL}/shows/search/{quote(title)}")
        if response.status_code != 200:
            return None
        shows: list[dict[str, Any]] = response.json().get("shows", [])
        target = normalize_show_name(title)
        exact = [show for show in shows if normalize_show_name(show["name"]) == target]
        if exact:
            return max(exact, key=lambda show: show.get("nbSeasons", 0))
        return shows[0] if shows else None
