from typing import no_type_check

from subsearch.providers import common_utils


class AdvTitleSearch:
    def __init__(self, title: str, year: int) -> None:
        self.title = title
        self.year = year

    def get_url(self) -> str:
        imdb_domain = "https://www.imdb.com"
        return f"{imdb_domain}/search/title/?{self.title_search}&{self.release_date_search}"

    @property
    def prior_year(self) -> str:
        return f"{self.year-1}-01-01"

    @property
    def release_year(self) -> str:
        return f"{self.year}-12-31"

    @property
    def release_title(self) -> str:
        return self.title.replace(" ", "+")

    @property
    def title_search(self) -> str:
        return f"title={self.release_title}"

    @property
    def release_date_search(self) -> str:
        return f"release_date={self.prior_year},{self.release_year}"


class FindImdbID(AdvTitleSearch):
    @no_type_check
    def __init__(self, title: str, year: int) -> None:
        self.title = title.lower()
        self.year = year
        self.id = None

        adv_search = AdvTitleSearch(self.title, self.year)

        url = adv_search.get_url()
        tree = common_utils.get_html_parser(url)

        product = tree.css("a.ipc-title-link-wrapper h3.ipc-title__text")

        for item in product:
            href_ = item.parent.attrs["href"]
            imdb_id = href_.split("/")[2]
            title_ = item.text().split(". ")[-1]
            _year = item.parent.parent.next.child.child.html
            release_year = self._handle_ongoing_show(_year)

            if self.title != title_.lower():
                continue

            if self.year != release_year and (self.year - 1) != release_year:
                continue

            self.id = imdb_id
            break

    def _handle_ongoing_show(self, year: str) -> int:
        release_year = year.split("–")[0]
        return int(release_year)
