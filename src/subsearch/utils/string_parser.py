import re

from num2words import num2words

from subsearch.data.data_objects import AppConfig, ProviderUrls, ReleaseMetadata
from subsearch.utils import imdb


def find_year(string: str) -> int:
    re_year = re.findall("^.*\.([1-2][0-9]{3})\.", string)  # https://regex101.com/r/r5TwxJ/1
    if re_year:
        year = re_year[0]
        return int(year)
    return 0000


def find_title_by_year(string: str) -> str:
    re_title = re.findall("^(.*)\.[1-2][0-9]{3}\.", string)  # https://regex101.com/r/FKUpY0/1
    if re_title:
        title: str = re_title[0]
        title = title.replace(".", " ")
        return title
    return "N/A"


def find_title_by_show(string: str) -> str:
    re_title = re.findall("^(.*)\.[s]\d*[e]\d*\.", string)  # https://regex101.com/r/41OZE5/1
    if re_title:
        title: str = re_title[0]
        title = title.replace(".", " ")
        return title
    return "N/A"


def find_season_episode(string: str) -> str:
    re_se = re.findall("\.([s]\d*[e]\d*)\.", string)  # https://regex101.com/r/8Nwlr6/1
    if re_se:
        se: str = re_se[0]
        return se
    return "N/A"


def convert_to_ordinal_string(string: str) -> tuple[str, str, str, str, bool]:
    if string == "N/A":
        season, season_ordinal, episode, episode_ordinal = "N/A", "N/A", "N/A", "N/A"
        show_bool = False
    else:
        season, episode = string.replace("s", "").replace("e", " ").split(" ")
        season_ordinal = num2words(int(season), lang="en", to="ordinal")
        episode_ordinal = num2words(int(episode), lang="en", to="ordinal")
        show_bool = True
    return season, season_ordinal, episode, episode_ordinal, show_bool


def find_group(string: str) -> str:
    group = string.rsplit("-", 1)[-1]
    return group


def find_title(filename: str, year: int, series: bool):
    if year != 0000:
        title = find_title_by_year(filename)
    elif series and year == 0000:
        title = find_title_by_show(filename)
    else:
        title = filename.rsplit("-", 1)[0]
    return title


class CreateProviderUrls:
    """
    Class for retrieving initial URL to search with for a provider
    """

    def __init__(self, file_hash: str, app_config: AppConfig, release_metadata: ReleaseMetadata):
        """
        Get initial URL to search with for a provider

        Args:
            file_hash (str): _description_
            app_config (AppConfig): _description_
            release_metadata (ReleaseMetadata): _description_
        """
        self.file_hash = file_hash
        self.app_config = app_config
        self.release_metadata = release_metadata

    def retrieve_urls(self) -> ProviderUrls:
        """
        Retrieve all available URLs

        Returns:
            ProviderUrls: URLs for all providers
        """
        return ProviderUrls(self.subscene(), self.opensubtitles(), self.opensubtitles_hash(), self.yifysubtitles())

    def subscene(self) -> str:
        """
        subscene URL

        Returns:
            str: f"{domain}/{query}={search_parameters}"
        """
        domain = "https://subscene.com"
        query = "subtitles/searchbytitle?query"
        search_parameters = self._subscene_search_parameters()
        url_subscene = f"{domain}/{query}={search_parameters}"
        return url_subscene.replace(" ", "%20")

    def opensubtitles(self) -> str:
        """
        opensubtitles URL

        Returns:
            str: f"{domain}/{subtitle_type}/{search_parameters}/rss_2_00"
        """
        domain = "https://www.opensubtitles.org"
        subtitle_type = self._opensubtitles_subtitle_type()
        search_parameters = self._opensubtitles_search_parameters()
        return f"{domain}/{subtitle_type}/{search_parameters}/rss_2_00".replace(" ", "%20")

    def opensubtitles_hash(self) -> str:
        """
        opensubtitles URL

        Returns:
            str: f"{domain}/{subtitle_type}/moviehash-{self.file_hash}"
        """
        domain = "https://www.opensubtitles.org"
        subtitle_type = self._opensubtitles_subtitle_type()
        return f"{domain}/{subtitle_type}/moviehash-{self.file_hash}"

    def yifysubtitles(self) -> str:
        """
        yifysubtitles URL

        Returns:
            str: f"{domain}/movie-imdb/{tt_id}"
        """
        if self.release_metadata.tvseries:
            return "N/A"
        domain = "https://yifysubtitles.org"
        tt_id = imdb.FindImdbID(self.release_metadata.title, self.release_metadata.year).id
        return f"{domain}/movie-imdb/{tt_id}" if tt_id is not None else "N/A"

    def _subscene_search_parameters(self) -> str:
        if self.release_metadata.tvseries:
            return f"{self.release_metadata.title} - {self.release_metadata.season_ordinal} season"
        return f"{self.release_metadata.title}"

    def _opensubtitles_subtitle_type(self) -> str:
        if self.app_config.hearing_impaired and self.app_config.non_hearing_impaired is False:
            return f"en/search/sublanguageid-{self.app_config.language_iso_639_3}/hearingimpaired-on"
        return f"en/search/sublanguageid-{self.app_config.language_iso_639_3}"

    def _opensubtitles_search_parameters(self) -> str:
        if self.release_metadata.tvseries:
            return f"searchonlytvseries-on/season-{self.release_metadata.season}/episode-{self.release_metadata.episode}/moviename-{self.release_metadata.title}"
        return f"searchonlymovies-on/moviename-{self.release_metadata.title} ({self.release_metadata.year})"


def get_release_metadata(filename: str, file_hash: str) -> ReleaseMetadata:
    """
    Get release metadata from a filename
    Uses regex expressions to find the parameters

    Args:
        filename (str): release name from the filename
        file_hash (str): hash of the file

    Returns:
        ReleaseMetadata: title, year, season, season_ordinal, episode, episode_ordinal, tv_series, release name, group, file_hash
    """
    filename = filename.lower()
    year = find_year(filename)
    season_episode = find_season_episode(filename)
    season, season_ordinal, episode, episode_ordinal, series = convert_to_ordinal_string(season_episode)

    title = find_title(filename, year, series)
    group = find_group(filename)

    parameters = ReleaseMetadata(
        title,
        year,
        season,
        season_ordinal,
        episode,
        episode_ordinal,
        series,
        filename,
        group,
        file_hash,
    )
    return parameters


def calculate_match(from_user: str, from_website: str) -> int:
    """
    Compare two strings and compare how closely they match against each other

    Args:
        from_user (str): release from filename
        from_browser (str): release from the provider

    Returns:
        int: _description_
    """
    max_percentage = 100
    _from_user: list[str] = mk_lst(from_user)
    _from_website: list[str] = mk_lst(from_website)
    lst1, lst2 = make_equal_size(_from_user, _from_website)
    not_matching = list(set(lst1) - set(lst2))
    not_matching_value = len(not_matching)
    number_of_items = len(lst1)
    percentage_to_remove = round(not_matching_value / number_of_items * max_percentage)
    pct = round(max_percentage - percentage_to_remove)

    return pct


def mk_lst(release: str) -> list[str]:
    """
    Create a list from a string

    Args:
        release (str)

    Returns:
        list[str]
    """
    new: list[str] = []
    qualities = ["720p", "1080p", "1440p", "2160p"]
    temp = release.split(".")

    for item in temp:
        if item not in qualities:
            new.append(item.lower())
    return new


def make_equal_size(lst1, lst2):
    if len(lst1) == len(lst2):
        return lst1, lst2
    elif len(lst1) > len(lst2):
        lst_big, lst_small = lst1, lst2
    else:
        lst_big, lst_small = lst2, lst1

    num_big, num_small = sorted((len(lst1), len(lst2)), reverse=True)
    difference = num_big - num_small
    filled_list = fill_shorter_list(lst_big, lst_small, difference)
    return lst_big, filled_list


def fill_shorter_list(big_lst, small_lst, difference):
    if big_lst > small_lst:
        for _i in range(difference):
            small_lst.append(None)
    return small_lst
