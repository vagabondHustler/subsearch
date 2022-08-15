from dataclasses import dataclass

from num2words import num2words


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


def split_last_hyphen(string: str) -> str:
    """
    Split last hyphen in a string, keep last part of the string

    Args:
        string (str): any string with a hyphen

    Returns:
        str: last item in the list of the string split by hyphen
    """
    group = string.rsplit("-", 1)[-1]
    return group


def get_parameters(file_name: str, file_hash: str, lang_abbr: str) -> SearchParameters:
    """
    Parse file name and get parameters for searching on subscene and opensubtitles

    Args:
        file_name (str): name of the file
        file_hash (str): hash of the file
        lang_abbr (str): language abbreviation for ordinal numbers

    Returns:
        SearchParameters: title, year, season, season_ordinal, episode, episode_ordinal, tv_series, release, group
    """
    # default values
    title = "N/A"
    year = "N/A"
    season = "N/A"
    season_ordinal = "N/A"
    episode = "N/A"
    episode_ordinal = "N/A"
    group = "N/A"
    tv_series = False
    year_found = False

    release = file_name

    # find season, episode, make it ordinal and set tv_series to true if it is a tv-series
    for item in release.lower().split("."):
        if item.startswith("s") and item[-1].isdigit() and "e" in item:
            season, episode = item.replace("s", "").replace("e", " ").split(" ")
            season_ordinal = num2words(int(season), lang=lang_abbr, to="ordinal")
            episode_ordinal = num2words(int(episode), lang=lang_abbr, to="ordinal")
            if season[-1].isdigit():
                tv_series = True
                break

    string_list = release.lower().split(".")
    subtract = []
    # list is reversed if a year is apart of the title, like "2001: A Foo Bar" from 1991
    # this is to prevent the year from the title being used as the release year of the movie/show
    for item in string_list[::-1]:
        # if year is found everything else in the list should be the release name
        if year_found or item.startswith("s") and item[-1].isdigit():
            _title = (i for i in string_list if i not in subtract)
            break
        if item.isdigit() and len(item) == 4:
            year_found = True
            year = item
        subtract.append(item)

    if tv_series:
        title = " ".join(x for x in _title).replace(f"s{season}e{episode}", f"- {season_ordinal} season").strip()
    else:
        title = " ".join(x for x in _title)

    if "-" in release:
        group = split_last_hyphen(release)

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
