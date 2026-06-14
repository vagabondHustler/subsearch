from dataclasses import dataclass

import imdbinfo
from imdbinfo.exceptions import ImdbinfoError

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
    log.info(f"Connecting to IMDb to look up titles matching {typed_term!r}")
    try:
        search_result = imdbinfo.search_title(typed_term)
    except ImdbinfoError:
        log.warning(f"IMDb connection failed while fetching suggestions for {typed_term!r}")
        return []
    if not search_result:
        log.info(f"IMDb returned no suggestions for {typed_term!r}")
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
    log.info(f"IMDb returned {len(suggestions)} title suggestion(s) for {typed_term!r}")
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
            log.warning(f"IMDb connection failed while looking up {title!r}")
            self.diagnostic_status = ProviderDiagnosticStatus.STRUCTURE_INVALID
            return None
        if not search_result:
            log.debug(f"IMDb returned no results for {title!r}")
            return None

        for found_title in search_result.titles:
            if not self._title_matches(found_title.title):
                continue
            if self.tvseries and not self._is_tvseries(found_title.kind):
                continue
            if not self.tvseries and not self._year_matches(found_title.year):
                continue

            self.imdb_id = found_title.imdbId
            log.debug(f"IMDb matched {title!r} -> {self.imdb_id}")
            break
        else:
            log.debug(f"IMDb lookup found no matching entry for {title!r} ({year}, tvseries={tvseries})")

    def _title_matches(self, found_title: str) -> bool:
        return self.title == found_title.lower()

    def _is_tvseries(self, kind: str | None) -> bool:
        return kind == "tvSeries"

    def _year_matches(self, release_year: int | None) -> bool:
        if self.year == 0:
            # typed search term without a year: accept the first title match
            return True
        return self.year == release_year or (self.year - 1) == release_year
