import re
from dataclasses import dataclass
from typing import Any, Literal, Optional, Union

from num2words import num2words


def find_year(string: str) -> Union[int, str]:
    """
    Parse string from start, until last instance of a year between .1000-2999. found, keep last instance of year
    https://regex101.com/r/r5TwxJ/1

    Args:
        string (str): Title.Of.The.Movie.YEAR.Source.Codec-GROUP

    Returns:
        str: YEAR
    """
    # from start of string until number between 1000-2999 ending with. found
    _year = re.findall("^.*\.([1-2][0-9]{3})\.", string)
    if len(_year) > 0:
        year = _year[0]
        return int(year)
    return "N/A"


def find_title_by_year(string: str) -> str:
    """
    Parse string from start, until last instance of a year between .1000-2999. found, keep everything before last instance of .year
    https://regex101.com/r/FKUpY0/1

    Args:
        string (str): Title.Of.The.Movie.YEAR.Source.Codec-GROUP

    Returns:
        str: Title.Of.The.Movie
    """
    _title = re.findall("^(.*)\.[1-2][0-9]{3}\.", string)
    if len(_title) > 0:
        title: str = _title[0]
        title = title.replace(".", " ")
        return title
    return "N/A"


def find_title_by_show(string: str) -> str:
    """
    Parse string from start, until last instance of .s00e00. found, keep everything before .season
    https://regex101.com/r/41OZE5/1

    Args:
        string (str): Title.Of.The.Show.s01e01.Source.Codec-GROUP

    Returns:
        str: Title.Of.The.Show
    """
    _title = re.findall("^(.*)\.[s]\d*[e]\d*\.", string)
    if len(_title) > 0:
        title: str = _title[0]
        title = title.replace(".", " ")
        return title
    return "N/A"


def find_season_episode(string: str) -> str:
    """
    Parse string from start, until last instance of .s00e00. found, keep .s00e00.
    https://regex101.com/r/8Nwlr6/1

    Args:
        string (str): Title.Of.The.Show.s01e01.Source.Codec-GROUP

    Returns:
        str: s01e01
    """
    _se = re.findall("\.([s]\d*[e]\d*)\.", string)
    if len(_se) > 0:
        se: str = _se[0]
        return se
    return "N/A"


NA = tuple[Literal["N/A"], Literal["N/A"], Literal["N/A"], Literal["N/A"], Literal[False]]


def find_ordinal(string: str, lang_code2: str) -> Union[tuple[str, str, str, str, bool], NA]:
    """
    Convert numbers into ordinal strings, 01 = First, 02 = Second...

    Args:
        string (str): s01e01
        lang_abbr (str): abbreviation of ordinal language

    Returns:
        str | int: _description_
    """
    if string == "N/A":
        season, season_ordinal, episode, episode_ordinal = "N/A", "N/A", "N/A", "N/A"
        show_bool = False

        return season, season_ordinal, episode, episode_ordinal, show_bool
    else:
        season, episode = string.replace("s", "").replace("e", " ").split(" ")
        season_ordinal = num2words(int(season), lang=lang_code2, to="ordinal")
        episode_ordinal = num2words(int(episode), lang=lang_code2, to="ordinal")
        show_bool = True
        return season, season_ordinal, episode, episode_ordinal, show_bool


def find_group(string: str) -> str:
    group = string.rsplit("-", 1)[-1]
    return group


@dataclass(frozen=True, order=True)
class SearchParameters:
    url_subscene: str
    url_opensubtitles: str
    title: str
    year: Union[int, str]
    season: str
    season_ordinal: str
    episode: str
    episode_ordinal: str
    show_bool: bool
    release: str
    group: str
    file_hash: Optional[str]


def get_parameters(filename: str, file_hash: Optional[str], language: str, lang_code2: str) -> SearchParameters:
    """
    Parse filename and get parameters for searching on subscene and opensubtitles
    Uses regex expressions to find the parameters

    Args:
        file_name (str): name of the file
        file_hash (str): hash of the file
        lang_abbr (str): language abbreviation for ordinal numbers

    Returns:
        SearchParameters: title, year, season, season_ordinal, episode, episode_ordinal, tv_series, release, group
    """
    filename = filename.lower()
    lang_code3 = language[:3].lower()

    year = find_year(filename)

    season_episode = find_season_episode(filename)
    season, season_ordinal, episode, episode_ordinal, show_bool = find_ordinal(season_episode, lang_code2)

    if year != "N/A":
        title = find_title_by_year(filename)
    elif show_bool and year == "N/A":
        title = find_title_by_show(filename)
        title = f"{title} - {season_ordinal} season"
    else:
        title = filename.rsplit("-", 1)[0]

    group = find_group(filename)
    subscene = "https://subscene.com/subtitles/searchbytitle?query="
    opensubtitles = f"https://www.opensubtitles.org/en/search/sublanguageid-{lang_code3}/moviename-"
    url_subscene = f"{subscene}{title}".replace(" ", "%20")
    url_opensubtitles = f"{opensubtitles}{file_hash}"

    parameters = SearchParameters(
        url_subscene,
        url_opensubtitles,
        title,
        year,
        season,
        season_ordinal,
        episode,
        episode_ordinal,
        show_bool,
        filename,
        group,
        file_hash,
    )
    return parameters


def get_pct_value(from_pc: Any, from_browser: Any) -> int:
    """
    Parse two lists and return match in %

    Args:
        from_pc (str | int): list from pc
        from_browser (str | int): list from browser
    Returns:
        int: value in percentage of how many words match
    """
    max_percentage = 100
    pc_list: list[Any] = mk_lst(from_pc)
    browser_list: list[Any] = mk_lst(from_browser)
    not_matching = list(set(pc_list) - set(browser_list))
    not_matching_value = len(not_matching)
    number_of_items = len(pc_list)
    percentage_to_remove = round(not_matching_value / number_of_items * max_percentage)
    pct = round(max_percentage - percentage_to_remove)

    return pct


# create list from string
def mk_lst(release: Any) -> list[Any]:
    new: list[Any] = []
    qualities = ["720p", "1080p", "1440p", "2160p"]
    temp = release.split(".")

    for item in temp:
        if item not in qualities:
            new.append(item.lower())
    return new
