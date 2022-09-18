import re
from dataclasses import dataclass
from typing import Any, Literal, Union

import imdb
from num2words import num2words

from subsearch.utils.raw_config import UserParameters


def find_year(string: str) -> int:
    re_year = re.findall("^.*\.([1-2][0-9]{3})\.", string)  # https://regex101.com/r/r5TwxJ/1
    if len(re_year) > 0:
        year = re_year[0]
        return int(year)
    return 0000


def find_title_by_year(string: str) -> str:
    re_title = re.findall("^(.*)\.[1-2][0-9]{3}\.", string)  # https://regex101.com/r/FKUpY0/1
    if len(re_title) > 0:
        title: str = re_title[0]
        title = title.replace(".", " ")
        return title
    return "N/A"


def find_title_by_show(string: str) -> str:
    re_title = re.findall("^(.*)\.[s]\d*[e]\d*\.", string)  # https://regex101.com/r/41OZE5/1
    if len(re_title) > 0:
        title: str = re_title[0]
        title = title.replace(".", " ")
        return title
    return "N/A"


def find_season_episode(string: str) -> str:
    re_se = re.findall("\.([s]\d*[e]\d*)\.", string)  # https://regex101.com/r/8Nwlr6/1
    if len(re_se) > 0:
        se: str = re_se[0]
        return se
    return "N/A"


def find_ordinal(string: str) -> tuple[str, str, str, str, bool]:
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


def find_imdb_tt_id(base_yts: str, title: str, year: int) -> str:
    ia = imdb.Cinemagoer()
    movies = ia.search_movie(title)
    url_yifysubtitles = base_yts
    for movie in movies:
        movie_no_colon = movie.data["title"].replace(":", "").split("(")[0]
        if movie_no_colon.lower() != title.lower():
            continue
        if movie.data["year"] != year or movie.data["year"] != year - 1:
            continue
        _movie_id: str = movie.movieID
        tt_id = f"tt{_movie_id}"
        url_yifysubtitles = f"{base_yts}/{tt_id}"
        break
    return url_yifysubtitles


@dataclass(frozen=True, order=True)
class FileSearchParameters:
    url_subscene: str
    url_opensubtitles: str
    url_opensubtitles_hash: str
    url_yifysubtitles: str
    title: str
    year: int
    season: str
    season_ordinal: str
    episode: str
    episode_ordinal: str
    series: bool
    release: str
    group: str
    file_hash: str
    definitive_match: str


def get_parameters(filename: str, file_hash: str, user_parameters: UserParameters) -> FileSearchParameters:
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

    lang_code3 = user_parameters.languages[user_parameters.current_language]
    year = find_year(filename)
    season_episode = find_season_episode(filename)
    season, season_ordinal, episode, episode_ordinal, series = find_ordinal(season_episode)

    if year != 0000:
        title = find_title_by_year(filename)
    elif series and year == 0000:
        title = find_title_by_show(filename)
    else:
        title = filename.rsplit("-", 1)[0]

    group = find_group(filename)

    base_ss = "https://subscene.com/subtitles/searchbytitle?query="
    base_yts = "https://yifysubtitles.org/movie-imdb"

    if user_parameters.hearing_impaired and user_parameters.non_hearing_impaired is False:
        base_os = f"https://www.opensubtitles.org/en/search/sublanguageid-{lang_code3}/hearingimpaired-on"
    else:
        base_os = f"https://www.opensubtitles.org/en/search/sublanguageid-{lang_code3}"

    url_opensubtitles_hash = f"{base_os}/moviehash-{file_hash}"

    if series:
        url_subscene = f"{base_ss}{title} - {season_ordinal} season"
        url_opensubtitles = f"{base_os}/searchonlytvseries-on/season-{season}/episode-{episode}/moviename-{title}/rss_2_00"
        url_yifysubtitles = "N/A"
    else:
        url_subscene = f"{base_ss}{title} ({year})"
        url_opensubtitles = f"{base_os}/searchonlymovies-on/moviename-{title} ({year})/rss_2_00"
        url_yifysubtitles = find_imdb_tt_id(base_yts, title, year)

    definitive_match = url_subscene.rsplit("query=", 1)[-1]

    url_subscene = url_subscene.replace(" ", "%20")
    url_opensubtitles = url_opensubtitles.replace(" ", "%20")

    parameters = FileSearchParameters(
        url_subscene,
        url_opensubtitles,
        url_opensubtitles_hash,
        url_yifysubtitles,
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
        definitive_match,
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


def mk_lst(release: Any) -> list[Any]:
    # create list from string
    new: list[Any] = []
    qualities = ["720p", "1080p", "1440p", "2160p"]
    temp = release.split(".")

    for item in temp:
        if item not in qualities:
            new.append(item.lower())
    return new
