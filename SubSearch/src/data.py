import json
from dataclasses import dataclass
from num2words import num2words


@dataclass
class ConfigData:
    language: str
    hearing_impaired: str
    languages: list[str]
    video_ext: list
    precentage_pass: int
    terminal_focus: str
    context_menu_icon: str


def read_data(config_file: str) -> ConfigData:
    with open(config_file, encoding="utf-8") as file:
        data = json.load(file)
        return ConfigData(**data)


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
    tv_series: bool
    release: str
    group: str
    file_hash: str


def split_last_hyphen(character: str, string: str) -> str:
    group = string.rsplit(character, 1)[-1]
    return group


# get all the parameters needed to scrape, from file or directory name
def get_parameters(directory_path: str, language_abbr: str, file_hash: str, video_release_name: str = None) -> SearchParameters:
    _tmp: list = []
    if video_release_name is None:
        directory_name = directory_path.split("\\")
        # release and group
        release = directory_name[-1]
    elif video_release_name is not None:
        release = video_release_name.replace(" ", ".")
    if "-" in release:
        group = split_last_hyphen("-", release)
    else:
        group = "N/A"
    items = release.split(".")
    # url, title, season, and year
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
            url_subscene = f"https://subscene.com/subtitles/searchbytitle?query={title}".replace(" ", "%20")
            url_opensubtitles = f"https://www.opensubtitles.org/en/search/sublanguageid-all/moviehash-{file_hash}"
            year = "N/A"

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
