import re
from dataclasses import dataclass
from typing import Any, Literal

from num2words import num2words


def find_year(string: str) -> str:
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
        return year
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
        title = _title[0]
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
        title = _title[0]
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
        se = _se[0]
        return se
    return "N/A"


ordinal_return = (
    tuple[Literal["N/A"], Literal["N/A"], Literal["N/A"], Literal["N/A"], Literal[False]]
    | tuple[str, Any, str, Any, Literal[True]]
)


def find_ordinal(string: str, lang_abbr: str) -> ordinal_return:
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

    season, episode = string.replace("s", "").replace("e", " ").split(" ")
    season_ordinal = num2words(int(season), lang=lang_abbr, to="ordinal")
    episode_ordinal = num2words(int(episode), lang=lang_abbr, to="ordinal")
    show_bool = True
    return season, season_ordinal, episode, episode_ordinal, show_bool


def find_group(string: str) -> str:
    group = string.rsplit("-", 1)[-1]
    return group


@dataclass
class SearchParameters:
    url_subscene: str
    url_opensubtitles: str
    title: str
    year: int
    season: str
    season_ordinal: str
    episode: str
    episode_ordinal: str
    show_bool: bool
    release: str
    group: str
    file_hash: str


def get_parameters(filename: str, file_hash: str, lang_abbr: str) -> SearchParameters:
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

    year = find_year(filename)
    if year.isnumeric():
        title = find_title_by_year(filename)

    season_episode = find_season_episode(filename)
    season, season_ordinal, episode, episode_ordinal, show_bool = find_ordinal(season_episode, lang_abbr)

    if show_bool:
        title = find_title_by_show(filename)
        title = f"{title} - {season_ordinal} season"

    group = find_group(filename)

    try:
        title
    except UnboundLocalError:
        title = filename.rsplit("-", 1)[0]

    subscene = "https://subscene.com/subtitles/searchbytitle?query="
    opensubtitles = "https://www.opensubtitles.org/en/search/sublanguageid-eng/moviename-"
    url_subscene = f"{subscene}{title}".replace(" ", "%20")
    url_opensubtitles = f"{opensubtitles}{file_hash}"

    parameters = {
        "url_subscene": url_subscene,
        "url_opensubtitles": url_opensubtitles,
        "title": title,
        "year": year,
        "season": season,
        "season_ordinal": season_ordinal,
        "episode": episode,
        "episode_ordinal": episode_ordinal,
        "show_bool": show_bool,
        "release": filename,
        "group": group,
        "file_hash": file_hash,
    }
    return SearchParameters(**parameters)
