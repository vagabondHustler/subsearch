import json
from dataclasses import dataclass


@dataclass
class UserData:
    language: str
    user_settings: list


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
    episode: str
    tv_series: bool
    release: str
    group: str


def get_parameters(directory_path: str) -> SearchParameters:
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
            season_episode = item.split("e")
            season, episode = season_episode[0], f"e{season_episode[1]}"
            if season[-1].isdigit():
                tv_series = True
                break
        else:
            season, episode = "N/A", "N/A"
            tv_series = False
            _tmp.append(item)
            title = " ".join(_tmp)
            url = f"https://subscene.com/subtitles/searchbytitle?query={title}"
            year = "N/A"

    data = {
        "url": url,
        "title": title,
        "year": year,
        "season": season,
        "episode": episode,
        "tv_series": tv_series,
        "release": release,
        "group": group,
    }
    return SearchParameters(**data)
