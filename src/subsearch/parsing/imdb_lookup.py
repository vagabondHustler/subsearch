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
