import json
from dataclasses import dataclass
from num2words import num2words


@dataclass
class UserData:
    language: str
    languages: list[str]
    precentage_pass: int
    terminal_focus: str
    terminal_in: str
    context_menu_icon: str


def read_data(config_file: str) -> UserData:

    with open(config_file, encoding="utf-8") as file:
        data = json.load(file)
        return UserData(**data)


@dataclass
class SearchParameters:
    url: str
    title: str
    year: int
    season: str
    season_ordinal: str
    episode: str
    episode_ordinal: str
    tv_series: bool
    release: str
    group: str


def get_parameters(directory_path: str, language_abbr: str) -> SearchParameters:
    _tmp: list = []
    directory_name = directory_path.split("\\")

    # release and group
    release = directory_name[-1]
    if "-" in release:
        _group = release.split("-")
        group = _group[-1]
    else:
        _group = release.split(".")
        group = _group[-1]
    items = release.split(".")
    # url, title and year
    for item in items:
        if item[0].isdigit() and len(item) == 4:
            year = item
            break
        elif item.startswith("s") and item[-1].isdigit():
            _season_episode = item.replace("s", "").replace("e", " ")
            season_episode = _season_episode.split(" ")
            sint, eint = season_episode[0], season_episode[1]
            season, episode = f"s{sint}", f"e{eint}"
            season_ordinal, episode_ordinal = (num2words(sint, lang=language_abbr, to="ordinal"), num2words(eint, lang=language_abbr, to="ordinal"))
            if season[-1].isdigit():
                tv_series = True
                break
        else:
            season, episode, season_ordinal, episode_ordinal = "N/A", "N/A", "N/A", "N/A"
            tv_series = False
            _tmp.append(item)
            title = " ".join(_tmp)
            url = f"https://subscene.com/subtitles/searchbytitle?query={title}"
            year = "N/A"

    parameters = {
        "url": url,
        "title": title,
        "year": year,
        "season": season,
        "season_ordinal": season_ordinal,
        "episode": episode,
        "episode_ordinal": episode_ordinal,
        "tv_series": tv_series,
        "release": release,
        "group": group,
    }
    return SearchParameters(**parameters)
