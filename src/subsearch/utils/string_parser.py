import re
from typing import Any

from num2words import num2words

from subsearch.data.constants import VIDEO_FILE
from subsearch.data.data_classes import (
    AppConfig,
    LanguageData,
    ProviderUrls,
    ReleaseData,
)
from subsearch.utils import imdb_lookup


def find_year(string: str) -> int:
    """
    Find and return the year from a string.

    Args:
        string (str): The string where the year has to be looked for.

    Returns:
        int: The first 4 digit number that matches the regex pattern or 0000 if no match is found.
    """
    re_year = re.findall("^.*\.([1-2][0-9]{3})\.", string)
    if re_year:
        year = re_year[0]
        return int(year)
    return 0000


def find_title_by_year(string: str) -> str:
    """
    Find and return the title of a media file by year.

    Args:
        string (str): The file name.

    Returns:
        str: The part of the file name before the year, with '.' replaced by ' ', or "" if no match is found.
    """
    re_title = re.findall("^(.*)\.[1-2][0-9]{3}\.", string)
    if re_title:
        title: str = re_title[0]
        title = title.replace(".", " ")
        return title
    return ""


def find_title_by_show(string: str) -> str:
    """
    Find and return the title of a media file by show.

    Args:
        string (str): The file name.

    Returns:
        str: The part of the filename before the season and episode values, with '.' replaced by ' ', or "" if no match is found.
    """
    re_title = re.findall("^(.*)\.[s]\d*[e]\d*\.", string)
    if re_title:
        title: str = re_title[0]
        title = title.replace(".", " ")
        return title
    return ""


def find_season_episode(string: str) -> str:
    """
    Find and return the season and episode values of a media file.

    Args:
        string (str): The file name.

    Returns:
        str: A string consisting of the season and episode values formatted like "s01e01", or "" if no match is found.
    """
    re_se = re.findall("\.([s]\d*[e]\d*)\.", string)
    if re_se:
        se: str = re_se[0]
        return se
    return ""


def convert_to_ordinal_string(string: str) -> tuple[str, str, str, str, bool]:
    """
    Converts the numeric TV series values (season and episode numbers) in a filename to their ordinal versions(if any).

    Args:
        string (str): The TV series values as pulled out from the filename as a single string, e.g., `s01e01`.

    Returns:
        tuple(str, str, str, str, bool): A tuple containing separated season and episode strings, corresponding ordinal
            strings, and a Boolean flag indicating whether the input string was matched successfully.
    """
    if string == "":
        season, season_ordinal, episode, episode_ordinal = "", "", "", ""
        show_bool = False
    else:
        season, episode = string.replace("s", "").replace("e", " ").split(" ")
        season_ordinal = num2words(int(season), lang="en", to="ordinal")
        episode_ordinal = num2words(int(episode), lang="en", to="ordinal")
        show_bool = True
    return season, season_ordinal, episode, episode_ordinal, show_bool


def find_group(string: str) -> str:
    """
    Find and return the group from a string.

    Args:
        string (str): The string where the group has to be looked for.

    Returns:
        str: The group identifier as taken from the end of the string.
    """
    group = string.rsplit("-", 1)[-1]
    return group


def find_title(filename: str, year: int, series: bool):
    """
    Find and return the media file's title, taking its year and/or TV series values into consideration.

    Args:
        filename (str): The name of the media file.
        year (int): The relevant year, extracted from the name, passed on from another method.
        series (bool): Whether the video file is a TV series or not.

    Returns:
        str: The name of the given media file.
    """
    if year != 0000:
        title = find_title_by_year(filename)
    elif series and year == 0000:
        title = find_title_by_show(filename)
    else:
        title = filename.rsplit("-", 1)[0]
    return title


class CreateProviderUrls:
    def __init__(self, app_config: AppConfig, release_data: ReleaseData, language_data: dict[str, Any]):
        """
        Initializes a new instance of the CreateProviderUrls class.

        Args:
            app_config (AppConfig): The application configuration
            release_metadata (ReleaseMetadata): The release metadata
        """
        self.app_config = app_config
        self.release_data = release_data
        self.language_data = language_data
        self.current_language_data: LanguageData = LanguageData(**language_data[app_config.language])

    def retrieve_urls(self) -> ProviderUrls:
        """
        Get the provider urls to search for subtitles.

        Returns:
            ProviderUrls: A collection of strings that contains urls to search for subtitles from different subtitle providers.
        """
        return ProviderUrls(self.subscene(), self.opensubtitles(), self.opensubtitles_hash(), self.yifysubtitles())

    def subscene(self) -> str:
        """
        Gets the Url for the Subscene website to search for subtitles.

        Returns:
            str: The url to search for subtitles on subscene.com
        """
        domain = "https://subscene.com"
        query = "subtitles/searchbytitle?query"
        search_parameters = self._subscene_search_parameters()
        url_subscene = f"{domain}/{query}={search_parameters}"
        return url_subscene.replace(" ", "%20")

    def opensubtitles(self) -> str:
        """
        Gets the Url for the Opensubtitles website to search for subtitles.

        Returns:
            str: The url to search for subtitles on opensubtitles.org
        """
        domain = "https://www.opensubtitles.org"
        subtitle_type = self._opensubtitles_subtitle_type()
        search_parameters = self._opensubtitles_search_parameters()
        return f"{domain}/{subtitle_type}/{search_parameters}/rss_2_00".replace(" ", "%20")

    def opensubtitles_hash(self) -> str:
        """
        Gets the Url to set a moviehash for the Opensubtitles website to find subtitles.

        Returns:
            str: the url to set moviehash for opensubtitles.org
        """
        domain = "https://www.opensubtitles.org"
        subtitle_type = self._opensubtitles_subtitle_type()
        return f"{domain}/{subtitle_type}/moviehash-{VIDEO_FILE.file_hash}"

    def yifysubtitles(self) -> str:
        """
        Gets the Url for the YifySubtitles website to search for subtitles for movies.

        Returns:
            str: The url to search for subtitles on yifysubtitles.org
        """
        if self.release_data.tvseries:
            return ""
        domain = "https://yifysubtitles.org"
        tt_id = imdb_lookup.FindImdbID(self.release_data.title, self.release_data.year).id
        return f"{domain}/movie-imdb/{tt_id}" if tt_id is not None else ""

    def _subscene_search_parameters(self) -> str:
        """
        Gets the search parameters for Subscene to search for the appropriate subtitles based on File name and season ordinal.

        Returns:
            str: The search parameter value for Subscene to search for the applicable subtitles.
        """
        if self.release_data.tvseries:
            return f"{self.release_data.title} - {self.release_data.season_ordinal} season"
        return f"{self.release_data.title}"

    def _opensubtitles_subtitle_type(self) -> str:
        """
        Gets the subtitle type and language settings for Opensubtitles based on Application configuration.

        Returns:
            str: The subtitle types and language configurations to search for subtitles in Opensubtitles.
        """
        alpha_2b = self.current_language_data.alpha_2b
        if self.app_config.hearing_impaired and self.app_config.non_hearing_impaired is False:
            return f"en/search/sublanguageid-{alpha_2b}/hearingimpaired-on"
        return f"en/search/sublanguageid-{alpha_2b}"

    def _opensubtitles_search_parameters(self) -> str:
        """
        Gets the search parameters for Opensubtitles to search for the appropriate subtitles based on Movie title, year, season and episode number.

        Returns:
            str: The search parameter value for Opensubtitles to search for the applicable subtitles.
        """
        if self.release_data.tvseries:
            return f"searchonlytvseries-on/season-{self.release_data.season}/episode-{self.release_data.episode}/moviename-{self.release_data.title}"
        return f"searchonlymovies-on/moviename-{self.release_data.title} ({self.release_data.year})"


def get_release_data(filename: str) -> ReleaseData:
    """
    Collects the necessary data from a filename.

    Args:
      filename (str): The name of the file to obtain release metadata from.

    Returns:
      ReleaseMetadata: A ReleaseMetadata object containing the relevant metadata for the inputted file.

    """
    release = filename.lower()
    year = find_year(release)
    season_episode = find_season_episode(release)
    season, season_ordinal, episode, episode_ordinal, series = convert_to_ordinal_string(season_episode)

    title = find_title(release, year, series)
    group = find_group(release)

    parameters = ReleaseData(
        title,
        year,
        season,
        season_ordinal,
        episode,
        episode_ordinal,
        series,
        release,
        group,
    )
    return parameters


def calculate_match(from_user: str, from_website: str) -> int:
    """
    Calculates the match between user input and website information

    Args:
        from_user (str): User input string
        from_website (str): Website information string

    Returns:
        int: The percentage of matching between two strings.
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


def valid_filename(input_string) -> bool:
    forbidden_characters_pattern = r'[<>:"/\\|?*\x00]'
    return bool(re.search(forbidden_characters_pattern, input_string))


def fix_filename(input_string) -> str:
    forbidden_characters_pattern = r'[<>:"/\\|?*\x00]'
    return re.sub(forbidden_characters_pattern, ".", input_string)


def valid_path(input_str, path_resolution) -> bool:
    if input_str == "":
        return False
    if path_resolution == "relative":
        pattern = r"^\.{1,2}\\([a-z0-9-_]|\\[a-z0-9-_])+$|^\.{1,2}$"
    elif path_resolution == "absolute":
        pattern = r"^[a-zA-Z]{1}:\\([a-z0-9-_]|\\[a-z0-9-_])+$"
    return bool(re.match(pattern, input_str))
