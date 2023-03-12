import re

from subsearch.providers import generic


class AdvTitleSearch:
    """
    A class representing an advanced title search.

    Attributes:
        title (str): The title of the movie or TV series.
        year (int): The release year of the movie or TV series.

    Methods:
        get_url(): Returns the URL for searching the given title and year on IMDb.

    Properties:
        prior_year: Returns a string with the start date of the previous year in ISO format.
        release_year: Returns a string with the end date of the current year in ISO format.
        release_title: Returns the title with spaces replaced by '+' signs for query purposes.
        title_search: Returns a string with the IMDB search parameter for the given title.
        release_date_search: Returns a string with the IMDB search parameter for the release date of the movie or TV series.
    """

    def __init__(self, title: str, year: int) -> None:
        """Initializes an instance of the AdvTitleSearch class."""
        self.title = title
        self.year = year

    def get_url(self) -> str:
        """Returns the URL for the advanced title search."""
        imdb_domain = "https://www.imdb.com"
        return f"{imdb_domain}/search/title/?{self.title_search}&{self.release_date_search}"

    @property
    def prior_year(self) -> str:
        """Returns a string with the start date of the previous year in ISO format."""
        return f"{self.year-1}-01-01"

    @property
    def release_year(self) -> str:
        """Returns a string with the end date of the current year in ISO format."""
        return f"{self.year}-12-31"

    @property
    def release_title(self) -> str:
        """Returns the title with spaces replaced by '+' signs for query purposes."""
        return self.title.replace(" ", "+")

    @property
    def title_search(self) -> str:
        """Returns a string with the IMDB search parameter for the given title."""
        return f"title={self.release_title}"

    @property
    def release_date_search(self) -> str:
        """Returns a string with the IMDB search parameter for the release date of the movie or TV series."""
        return f"release_date={self.prior_year},{self.release_year}"


class FindImdbID(AdvTitleSearch):
    """
    This class is used to find the IMDb ID of a movie or TV show based on its title and year.

    Args:
        title (str): The title of the movie or TV show.
        year (int): The year the movie or TV show was released.

    Attributes:
        title (str): The lowercased title of the movie or TV show.
        year (int): The year the movie or TV show was released.
        id (str or None): The IMDb ID of the movie or TV show if found. Otherwise, set to None.

    Methods:
        find_imdb_title: This method finds the title of a movie or TV show on IMDb.
        find_imdb_year: This method finds the year of release of a movie or TV show on IMDb.
        get_imdb_id: This method retrieves the IMDb ID of a movie or TV show from its page on IMDb.

    """

    def __init__(self, title: str, year: int):
        """Initializes FindImdbID with a title and year."""

        self.title = title.lower()
        self.year = year
        self.id = None

        adv_search = AdvTitleSearch(self.title, self.year)

        url = adv_search.get_url()
        tree = generic.get_html_parser(url)
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
        """
        Finds the title of a movie or TV show on IMDb.

        Returns:
            str: The title of the movie or TV show.
        """

        title = self.data.css_first("a").text()
        return title.lower()

    def find_imdb_year(self) -> int:
        """
        Finds the year of release of a movie or TV show on IMDb.

        Returns:
            int: The year the movie or TV show was released.
        """

        year = self.data.css_first("span.lister-item-year").child.text_content
        return int(re.findall("[0-9]+", year)[0])

    def get_imdb_id(self) -> str:
        """
        Retrieves the IMDb ID of a movie or TV show from its page on IMDb.

        Returns:
            str: The IMDb ID of the movie or TV show.
        """

        href = self.data.css_first("a")
        return re.findall("tt[0-9]+", href.attributes["href"])[0]
