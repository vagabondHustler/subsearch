import json
from dataclasses import dataclass

from num2words import num2words


@dataclass
class ConfigData:
    """
    Dataclass with current values from config.json
    """

    language: str
    hearing_impaired: str
    languages: list[str]
    video_ext: list
    percentage_pass: int
    terminal_focus: str
    context_menu_icon: str


def read_data(config_file: str) -> ConfigData:
    with open(config_file, encoding="utf-8") as file:
        data = json.load(file)
        return ConfigData(**data)


@dataclass
class SearchParameters:
    """
    Dataclass with all the necessary information from the media file
    """

    url_subscene: str
    url_opensubtitles: str
    title: str
    year: int
    season: str
    season_ordinal: str
    episode: str
    episode_ordinal: str
    tv_series: bool
    release: str
    group: str
    file_hash: str


def split_last_hyphen(string: str) -> str:
    group = string.rsplit("-", 1)[-1]
    return group


def find_title_year(x: str, year_found: bool = False) -> tuple:
    string_list = x.split(".")
    subtract = []
    # list is reversed if a year is apart of the title, like "2001: A Foo Bar" from 1991
    # this is to prevent the year from the title being used as the release year of the movie/show
    for item in string_list[::-1]:
        if year_found:
            _title = (i for i in string_list if i not in subtract)
            break
        if item.isdigit() and len(item) == 4:
            year_found = True
            year = item
        subtract.append(item)

    title = " ".join(x for x in _title)
    return title, year


def find_season_episode(string: str, lang_abbr: str) -> tuple:
    season, episode, season_ordinal, episode_ordinal, tv_series = "N/A", "N/A", "N/A", "N/A", False
    for item in string.lower().split("."):
        if item.startswith("s") and item[-1].isdigit():
            _season_episode = item.replace("s", "").replace("e", " ")
            season_episode = _season_episode.split(" ")
            sint, eint = season_episode[0], season_episode[1]
            season, episode = f"s{sint}", f"e{eint}"
            season_ordinal, episode_ordinal = (
                num2words(sint, lang=lang_abbr, to="ordinal"),
                num2words(eint, lang=lang_abbr, to="ordinal"),
            )
            if season[-1].isdigit():
                tv_series = True
                break
    return season, episode, season_ordinal, episode_ordinal, tv_series


def get_parameters(dir_path, lang_abbr, file_hash, file_name) -> SearchParameters:
    # if no file is found use the current directory path
    if file_name is None:
        release = dir_path.split("\\")[-1]
    else:
        release = file_name

    title, year = find_title_year(release)
    i = find_season_episode(release, lang_abbr)
    season, episode, season_ordinal, episode_ordinal, tv_series = i

    if "-" in release:
        _group = split_last_hyphen(release)
        group = _group[-1]
    else:
        group = "N/A"

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
        "tv_series": tv_series,
        "release": release,
        "group": group,
        "file_hash": file_hash,
    }
    return SearchParameters(**parameters)
