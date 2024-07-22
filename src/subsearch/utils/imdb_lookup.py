from typing import no_type_check

from subsearch.providers import common_utils


class AdvancedSearch:
    def __init__(self, *args, **kwargs) -> None: ...

    def get_url(self) -> str: ...


class ImdbMovieSearch(AdvancedSearch):
    def __init__(self, title: str, year: int, *args, **kwargs) -> None:
        super().__init__(self, *args, **kwargs)
        self.title = title
        self.year = year

    def get_url(self) -> str:
        imdb_domain = "https://www.imdb.com"
        return f"{imdb_domain}/search/title/?{self._title_search}&{self._release_date_search}"

    @property
    def _prior_year(self) -> str:
        return f"{self.year-1}-01-01"

    @property
    def _release_year(self) -> str:
        return f"{self.year}-12-31"

    @property
    def _release_title(self) -> str:
        return self.title.replace(" ", "+")

    @property
    def _title_search(self) -> str:
        return f"title={self._release_title}"

    @property
    def _release_date_search(self) -> str:
        return f"release_date={self._prior_year},{self._release_year}"


class ImdbTvseriesSearch(AdvancedSearch):
    def __init__(self, title: str, *args, **kwargs) -> None:
        super().__init__(self, *args, **kwargs)
        self.title = title

    def get_url(self) -> str:
        imdb_domain = "https://www.imdb.com"
        return f"{imdb_domain}/search/title/?{self._title_search}"

    @property
    def _release_title(self) -> str:
        return self.title.replace(" ", "+")

    @property
    def _title_search(self) -> str:
        return f"title={self._release_title}"


class FindImdbID:
    @no_type_check
    def __init__(self, title: str, year: int, tvseries: bool, request_timeout=(4, 8)) -> None:
        self.title = title.lower()
        self.year = year
        self.tvseries = tvseries
        self.imdb_id = ""
        adv_search = self._advanced_search()

        url = adv_search.get_url()
        tree = common_utils.request_parsed_response(url=url, timeout=request_timeout)
        if not tree:
            return None

        product = tree.css("a.ipc-title-link-wrapper h3.ipc-title__text")

        for item in product:
            href_ = item.parent.attrs["href"]
            imdb_id = href_.split("/")[2]
            title_ = item.text().split(". ")[-1]
            _year = item.parent.parent.next.child.child.html
            release_year = self._handle_ongoing_show(_year)

            if self.title != title_.lower():
                continue
            if not self.tvseries:
                if self.year != release_year and (self.year - 1) != release_year:
                    continue

            self.imdb_id = str(imdb_id)
            break

    def _advanced_search(self) -> AdvancedSearch:
        if self.tvseries:
            return ImdbTvseriesSearch(self.title)
        else:
            return ImdbMovieSearch(self.title, self.year)

    def _handle_ongoing_show(self, year: str) -> int:
        if not self.tvseries:
            release_year = year.split("–")[0]
            return int(release_year)
