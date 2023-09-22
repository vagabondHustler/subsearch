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
    re_year = re.findall("^.*\.([1-2][0-9]{3})\.", string)
    if re_year:
        year = re_year[0]
        return int(year)
    return 0000


def find_title_by_year(string: str) -> str:
    re_title = re.findall("^(.*)\.[1-2][0-9]{3}\.", string)
    if re_title:
        title: str = re_title[0]
        title = title.replace(".", " ")
        return title
    return ""


def find_title_by_show(string: str) -> str:
    re_title = re.findall("^(.*)\.[s]\d*[e]\d*\.", string)
    if re_title:
        title: str = re_title[0]
        title = title.replace(".", " ")
        return title
    return ""


def find_season_episode(string: str) -> str:
    re_se = re.findall("\.([s]\d*[e]\d*)\.", string)
    if re_se:
        se: str = re_se[0]
        return se
    return ""


def convert_to_ordinal_string(string: str) -> tuple[str, str, str, str, bool]:
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
    def __init__(self, app_config: AppConfig, release_data: ReleaseData, language_data: dict[str, Any]):
        self.app_config = app_config
        self.release_data = release_data
        self.language_data = language_data
        self.current_language_data: LanguageData = LanguageData(**language_data[app_config.language])

    def retrieve_urls(self) -> ProviderUrls:
        return ProviderUrls(self.subscene(), self.opensubtitles(), self.opensubtitles_hash(), self.yifysubtitles())

    def subscene(self) -> str:
        domain = "https://subscene.com"
        query = "subtitles/searchbytitle?query"
        search_parameters = self._subscene_search_parameters()
        url_subscene = f"{domain}/{query}={search_parameters}"
        return url_subscene.replace(" ", "%20")

    def opensubtitles(self) -> str:
        domain = "https://www.opensubtitles.org"
        subtitle_type = self._opensubtitles_subtitle_type()
        search_parameters = self._opensubtitles_search_parameters()
        return f"{domain}/{subtitle_type}/{search_parameters}/rss_2_00".replace(" ", "%20")

    def opensubtitles_hash(self) -> str:
        domain = "https://www.opensubtitles.org"
        subtitle_type = self._opensubtitles_subtitle_type()
        return f"{domain}/{subtitle_type}/moviehash-{VIDEO_FILE.file_hash}"

    def yifysubtitles(self) -> str:
        if self.release_data.tvseries:
            return ""
        domain = "https://yifysubtitles.org"
        tt_id = imdb_lookup.FindImdbID(self.release_data.title, self.release_data.year).id
        return f"{domain}/movie-imdb/{tt_id}" if tt_id is not None else ""

    def _subscene_search_parameters(self) -> str:
        if self.release_data.tvseries:
            return f"{self.release_data.title} - {self.release_data.season_ordinal} season"
        return f"{self.release_data.title}"

    def _opensubtitles_subtitle_type(self) -> str:
        alpha_2b = self.current_language_data.alpha_2b
        hearing_imparied, hearing_imparied_foreign_parts, foreign_parts = self.subtitle_type_logic()
        if hearing_imparied:
            return f"en/search/sublanguageid-{alpha_2b}/hearingimpaired-on"
        elif foreign_parts:
            return f"en/search/sublanguageid-{alpha_2b}/foreignpartsonly-on"
        elif hearing_imparied_foreign_parts:
            return f"en/search/sublanguageid-{alpha_2b}/hearingimpaired-on/foreignpartsonly-on"
        else:
            return f"en/search/sublanguageid-{alpha_2b}"

    def _opensubtitles_search_parameters(self) -> str:
        if self.release_data.tvseries:
            return f"searchonlytvseries-on/season-{self.release_data.season}/episode-{self.release_data.episode}/moviename-{self.release_data.title}"
        return f"searchonlymovies-on/moviename-{self.release_data.title} ({self.release_data.year})"

    def subtitle_type_logic(self):
        hi_all_parts = (
            self.app_config.hearing_impaired
            and not self.app_config.non_hearing_impaired
            and not self.app_config.only_foreign_parts
        )
        hi_foreign_parts = (
            self.app_config.hearing_impaired
            and not self.app_config.non_hearing_impaired
            and self.app_config.only_foreign_parts
        )
        non_hi_foreign_parts = (
            not self.app_config.hearing_impaired
            and self.app_config.non_hearing_impaired
            and self.app_config.only_foreign_parts
        )
        return hi_all_parts, hi_foreign_parts, non_hi_foreign_parts


def get_release_data(filename: str) -> ReleaseData:
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
