import re

from subsearch.providers import generic


class AdvTitleSearch:
    def __init__(self, title: str, year: int) -> None:
        self.title = title
        self.year = year

    def get_url(self):
        imdb_domain = "https://www.imdb.com"
        return f"{imdb_domain}/search/title/?{self.title_search}&{self.release_date_search}"

    @property
    def prior_year(self):
        return f"{self.year-1}-01-01"

    @property
    def release_year(self):
        return f"{self.year}-12-31"

    @property
    def release_title(self):
        return self.title.replace(" ", "+")

    @property
    def title_search(self):
        return f"title={self.release_title}"

    @property
    def release_date_search(self):
        return f"release_date={self.prior_year},{self.release_year}"


class FindImdbID(AdvTitleSearch):
    def __init__(self, title: str, year: int):
        self.title = title.lower()
        self.year = year
        self.id = None
        adv_search = AdvTitleSearch(self.title, self.year)
        url = adv_search.get_url()
        doc = generic.get_lxml_doc(url)
        items = doc.find_all("div", class_="lister-item-content")
        for item in items:
            self.data = item.find("h3", class_="lister-item-header")
            if self.title != self.imdb_title:
                continue
            if self.year != self.imdb_year and (self.year - 1) != self.imdb_year:
                continue
            self.id = self.imdb_id
            break

    @property
    def imdb_title(self) -> str:
        title = self.data.contents[3].string
        return title.lower()

    @property
    def imdb_year(self) -> int:
        year = self.data.contents[5].string
        return int(re.findall("[0-9]+", year)[0])

    @property
    def imdb_id(self) -> str:
        href = self.data.contents[3].attrs["href"]
        return re.findall("tt[0-9]+", href)[0]
