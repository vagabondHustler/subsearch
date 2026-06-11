import imdbinfo
from imdbinfo.exceptions import ImdbinfoError

from subsearch.runtime.models.model import ProviderDiagnosticStatus


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
            self.diagnostic_status = ProviderDiagnosticStatus.STRUCTURE_INVALID
            return None
        if not search_result:
            return None

        for found_title in search_result.titles:
            if not self._title_matches(found_title.title):
                continue
            if self.tvseries and not self._is_tvseries(found_title.kind):
                continue
            if not self.tvseries and not self._year_matches(found_title.year):
                continue

            self.imdb_id = found_title.imdbId
            break

    def _title_matches(self, found_title: str) -> bool:
        return self.title == found_title.lower()

    def _is_tvseries(self, kind: str | None) -> bool:
        return kind == "tvSeries"

    def _year_matches(self, release_year: int | None) -> bool:
        if self.year == 0:
            # typed search term without a year: accept the first title match
            return True
        return self.year == release_year or (self.year - 1) == release_year
