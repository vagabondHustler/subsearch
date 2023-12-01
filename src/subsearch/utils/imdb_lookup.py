import re

from subsearch.providers import core_provider


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
    def __init__(self, title: str, year: int):
        self.title = title.lower()
        self.year = year
        self.id = None

        adv_search = AdvTitleSearch(self.title, self.year)

        url = adv_search.get_url()
        tree = core_provider.get_html_parser(url)

        product = tree.css("a.ipc-title-link-wrapper h3.ipc-title__text")

        for item in product:
            href_ = item.parent.attrs["href"]
            imdb_id = href_.split("/")[2]
            title_ = item.text().split(". ")[-1]
            year_ = int(item.parent.parent.next.child.child.html)

            if self.title != title_.lower():
                continue

            if self.year != year_ and (self.year - 1) != year_:
                continue

            self.id = imdb_id
            break
