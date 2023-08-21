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
        product = tree.select("div.lister-item-content")

        for item in product.matches:
            self.data = item.css_first("h3.lister-item-header")

            if self.title != self.find_imdb_title():
                continue

            if self.year != self.find_imdb_year() and (self.year - 1) != self.find_imdb_year():
                continue

            self.id = self.get_imdb_id()
            break

    def find_imdb_title(self) -> str:
        title = self.data.css_first("a").text()
        return title.lower()

    def find_imdb_year(self) -> int:
        year = self.data.css_first("span.lister-item-year").child.text_content
        return int(re.findall("[0-9]+", year)[0])

    def get_imdb_id(self) -> str:
        href = self.data.css_first("a")
        return re.findall("tt[0-9]+", href.attributes["href"])[0]
