from dataclasses import dataclass

import imdbinfo
from imdbinfo.exceptions import ImdbinfoError

from subsearch.runtime.models import ProviderDiagnosticStatus
from subsearch.runtime.recorder import LogLevel, capture

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
        capture(f"IMDb connection failed while fetching episodes for {imdb_id} season 1", level=LogLevel.WARNING)
        return []
    total_seasons = season_episodes.total_series_seasons or 0
    suggestions = [SeasonSuggestion(number=season) for season in range(1, total_seasons + 1)]
    capture(f"IMDb returned {len(suggestions)} season(s) and 0 episode(s) for {imdb_id}")
    return suggestions


def find_episode_suggestions(imdb_id: str, season: int) -> list[EpisodeSuggestion]:
    try:
        season_episodes = imdbinfo.get_episodes(imdb_id, season=season)
    except ImdbinfoError:
        capture(
            f"IMDb connection failed while fetching episodes for {imdb_id} season {season}",
            level=LogLevel.WARNING,
        )
        return []
    suggestions = [
        EpisodeSuggestion(season=season, number=episode.episode, title=episode.title or "")
        for episode in season_episodes.episodes
        if episode.episode
    ]
    capture(f"IMDb returned 0 season(s) and {len(suggestions)} episode(s) for {imdb_id}")
    return suggestions


def find_title_suggestions(typed_term: str, limit: int = SUGGESTION_LIMIT) -> list[TitleSuggestion]:
    capture(f"Fuzzy matching {typed_term!r}")
    try:
        search_result = imdbinfo.search_title(typed_term)
    except ImdbinfoError:
        capture(f"IMDb connection failed while fetching suggestions for {typed_term!r}", level=LogLevel.WARNING)
        return []
    if not search_result:
        capture(f"IMDb returned no suggestions for {typed_term!r}")
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
    capture(f"IMDb returned {len(suggestions)} title suggestion(s) for {typed_term!r}")
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
            capture(f"IMDb connection failed while looking up {title!r}", level=LogLevel.WARNING)
            self.diagnostic_status = ProviderDiagnosticStatus.STRUCTURE_INVALID
            return None
        if not search_result:
            capture(f"IMDb returned no results for {title!r}", level=LogLevel.DEBUG)
            return None

        for found_title in search_result.titles:
            if not self._title_matches(found_title.title):
                continue
            if self.tvseries and not self._is_tvseries(found_title.kind):
                continue
            if not self.tvseries and not self._year_matches(found_title.year):
                continue

            self.imdb_id = found_title.imdbId
            capture(f"IMDb matched {title!r} -> {self.imdb_id}", level=LogLevel.DEBUG)
            break
        else:
            capture(
                f"IMDb lookup found no matching entry for {title!r} ({year}, tvseries={tvseries})",
                level=LogLevel.DEBUG,
            )

    def _title_matches(self, found_title: str) -> bool:
        return self.title == found_title.lower()

    def _is_tvseries(self, kind: str | None) -> bool:
        return kind == "tvSeries"

    def _year_matches(self, release_year: int | None) -> bool:
        if self.year == 0:
            # typed search term without a year: accept the first title match
            return True
        return self.year == release_year or (self.year - 1) == release_year
