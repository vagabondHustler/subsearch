import re
from dataclasses import dataclass
from typing import Any, Literal, Union

import imdb
from num2words import num2words

from subsearch.data.data_fields import FileSearchData, ProviderUrlData, UserConfigData


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
        if movie.data["year"] != year and movie.data["year"] != year - 1:
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


def get_provider_urls(file_hash: str, ucf: UserConfigData, frd: FileSearchData) -> ProviderUrlData:
    """
    Parse data to apply to the provider urls

    Args:
        file_hash (str): hash of the video file
        ufc (UserConfigData): user configured settings
        frd (FileSearchData): parsed data from release name of a file

    Returns:
        ProviderUrlData: urls to the different providers
    """

    def _set_base_url():
        base_ss = "https://subscene.com"
        base_yts = "https://yifysubtitles.org"
        base_os = "https://www.opensubtitles.org"
        return base_ss, base_yts, base_os

    def _set_subtitle_type():
        if ucf.hearing_impaired and ucf.non_hearing_impaired is False:
            subtitle_type_os = f"en/search/sublanguageid-{ucf.language_code3}/hearingimpaired-on"
    else:
            subtitle_type_os = f"en/search/sublanguageid-{ucf.language_code3}"
        return subtitle_type_os

    def _set_series_url():
        url_subscene = f"{base_ss}/subtitles/searchbytitle?query={frd.title} - {frd.season_ordinal} season"
        url_opensubtitles = f"{base_os}/{sub_type_os}/searchonlytvseries-on/season-{frd.season}/episode-{frd.episode}/moviename-{frd.title}/rss_2_00"

        url_yifysubtitles = "N/A"
        return url_subscene, url_opensubtitles, url_yifysubtitles

    def _set_movie_url():

        url_subscene = f"{base_ss}/subtitles/searchbytitle?query={frd.title} ({frd.year})"
        url_opensubtitles = f"{base_os}/{sub_type_os}/searchonlymovies-on/moviename-{frd.title} ({frd.year})/rss_2_00"
        tt_id = find_imdb_tt_id(frd.title, frd.year)
        if tt_id is None:
            url_yifysubtitles = "N/A"
    else:
            url_yifysubtitles = f"{base_yts}/movie-imdb/{tt_id}"

        return url_subscene, url_opensubtitles, url_yifysubtitles

    base_ss, base_yts, base_os = _set_base_url()
    sub_type_os = _set_subtitle_type()
    if frd.series:
        url_subscene, url_opensubtitles, url_yifysubtitles = _set_series_url()
    else:
        url_subscene, url_opensubtitles, url_yifysubtitles = _set_movie_url()

    url_opensubtitles_hash = f"{base_os}/{sub_type_os}/moviehash-{file_hash}"
    # definitive_match = url_subscene.rsplit("query=", 1)[-1]

    url_subscene = url_subscene.replace(" ", "%20")
    url_opensubtitles = url_opensubtitles.replace(" ", "%20")
    parameters = ProviderUrlData(url_subscene, url_opensubtitles, url_opensubtitles_hash, url_yifysubtitles)
    return parameters

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
