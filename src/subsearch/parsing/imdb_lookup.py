from dataclasses import dataclass

import imdbinfo
from imdbinfo.exceptions import ImdbinfoError

from subsearch.runtime.logging.events import LogEvent
from subsearch.runtime.logging.logger import log
from subsearch.runtime.models import ProviderDiagnosticStatus

SUGGESTION_LIMIT = 5
_SUGGESTION_KINDS = {"movie", "tvSeries", "tvMiniSeries", "tvMovie"}


@dataclass(frozen=True)
class TitleSuggestion:
    title: str
    year: int
    tvseries: bool
    imdb_id: str

    def display_text(self) -> str:
        year_suffix = f" ({self.year})" if self.year else ""
        kind_suffix = "  ·  TV series" if self.tvseries else ""
        return f"{self.title}{year_suffix}{kind_suffix}"

    def search_term(self) -> str:
        if self.tvseries or not self.year:
            return self.title
        return f"{self.title} ({self.year})"


@dataclass(frozen=True)
class SeasonSuggestion:
    number: int

    def display_text(self) -> str:
        return f"Season {self.number}"


@dataclass(frozen=True)
class EpisodeSuggestion:
    season: int
    number: int
    title: str

    def display_text(self) -> str:
        title_suffix = f"  ·  {self.title}" if self.title else ""
        return f"Episode {self.number}{title_suffix}"


def find_season_suggestions(imdb_id: str) -> list[SeasonSuggestion]:
    try:
        season_episodes = imdbinfo.get_episodes(imdb_id, season=1)
    except ImdbinfoError:
        log.event(LogEvent.IMDB_EPISODES_FAILED, level="warning", imdb_id=imdb_id, season=1)
        return []
    total_seasons = season_episodes.total_series_seasons or 0
    suggestions = [SeasonSuggestion(number=season) for season in range(1, total_seasons + 1)]
    log.event(LogEvent.IMDB_EPISODES, imdb_id=imdb_id, seasons=len(suggestions), episodes=0)
    return suggestions


def find_episode_suggestions(imdb_id: str, season: int) -> list[EpisodeSuggestion]:
    try:
        season_episodes = imdbinfo.get_episodes(imdb_id, season=season)
    except ImdbinfoError:
        log.event(LogEvent.IMDB_EPISODES_FAILED, level="warning", imdb_id=imdb_id, season=season)
        return []
    suggestions = [
        EpisodeSuggestion(season=season, number=episode.episode, title=episode.title or "")
        for episode in season_episodes.episodes
        if episode.episode
    ]
    log.event(LogEvent.IMDB_EPISODES, imdb_id=imdb_id, seasons=0, episodes=len(suggestions))
    return suggestions


def find_title_suggestions(typed_term: str, limit: int = SUGGESTION_LIMIT) -> list[TitleSuggestion]:
    log.event(LogEvent.IMDB_CONNECTING, term=typed_term)
    try:
        search_result = imdbinfo.search_title(typed_term)
    except ImdbinfoError:
        log.event(LogEvent.IMDB_SUGGESTIONS_FAILED, level="warning", term=typed_term)
        return []
    if not search_result:
        log.event(LogEvent.IMDB_NO_SUGGESTIONS, term=typed_term)
        return []
    suggestions = [
        TitleSuggestion(
            title=found_title.title,
            year=found_title.year or 0,
            tvseries=found_title.kind in ("tvSeries", "tvMiniSeries"),
            imdb_id=found_title.imdbId,
        )
        for found_title in search_result.titles
        if found_title.kind in _SUGGESTION_KINDS
    ]
    log.event(LogEvent.IMDB_SUGGESTIONS, count=len(suggestions), term=typed_term)
    return suggestions[:limit]


class ImdbIdLookup:
    title: str
    year: int
    tvseries: bool
    imdb_id: str
    diagnostic_status: ProviderDiagnosticStatus

    def __init__(self, title: str, year: int, tvseries: bool) -> None:
        self.title = title.lower()
        self.year = year
        self.tvseries = tvseries
        self.imdb_id = ""
        self.diagnostic_status = ProviderDiagnosticStatus.OK

        try:
            search_result = imdbinfo.search_title(title)
        except ImdbinfoError:
            log.event(LogEvent.IMDB_LOOKUP_FAILED, level="warning", title=title)
            self.diagnostic_status = ProviderDiagnosticStatus.STRUCTURE_INVALID
            return None
        if not search_result:
            log.event(LogEvent.IMDB_NO_RESULTS, level="debug", title=title)
            return None

        for found_title in search_result.titles:
            if not self._title_matches(found_title.title):
                continue
            if self.tvseries and not self._is_tvseries(found_title.kind):
                continue
            if not self.tvseries and not self._year_matches(found_title.year):
                continue

            self.imdb_id = found_title.imdbId
            log.event(LogEvent.IMDB_MATCHED, level="debug", title=title, imdb_id=self.imdb_id)
            break
        else:
            log.event(LogEvent.IMDB_NO_MATCH, level="debug", title=title, year=year, tvseries=tvseries)

    def _title_matches(self, found_title: str) -> bool:
        return self.title == found_title.lower()

    def _is_tvseries(self, kind: str | None) -> bool:
        return kind == "tvSeries"

    def _year_matches(self, release_year: int | None) -> bool:
        if self.year == 0:
            # typed search term without a year: accept the first title match
            return True
        return self.year == release_year or (self.year - 1) == release_year
