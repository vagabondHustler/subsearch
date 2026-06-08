import re
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

from num2words import num2words

from subsearch.runtime.logging.logger import log
from subsearch.runtime.config.constants import VIDEO_FILE
from subsearch.runtime.models.model import (
    AppConfig,
    Language,
    ProviderUrls,
    ReleaseInfo,
)


def remove_padded_zero(x: str) -> str:
    lenght = len(x)
    if x.startswith("0") and lenght > 1:
        return str(x)[1:]
    return x


def find_year(string: str) -> int:
    re_year = re.findall(r"^.*\.([1-2][0-9]{3})\.", string)
    if re_year:
        year = re_year[0]
        return int(year)
    return 0


def find_title_by_year(string: str) -> str:
    re_title = re.findall(r"^(.*)\.[1-2][0-9]{3}\.", string)
    if re_title:
        title: str = re_title[0]
        title = title.replace(".", " ")
        return title
    return ""


def find_title_by_show(string: str) -> str:
    re_title = re.findall(r"^(.*)\.[s]\d*[e]\d*\.", string)
    if re_title:
        title: str = re_title[0]
        title = title.replace(".", " ")
        return title
    return ""


def find_season_episode(string: str) -> str:
    re_se = re.findall(r"\.([s]\d*[e]\d*)\.", string)
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


def find_title(filename: str, year: int, series: bool) -> str:
    if year != 0:
        title = find_title_by_year(filename)
    elif series and year == 0:
        title = find_title_by_show(filename)
    else:
        title = filename.rsplit("-", 1)[0]
    return title


_YIFY_MIRRORS: list[str] = [
    "https://yifysubtitles.ch",
    "https://yifysubtitles.mx",
    "https://yifysubtitles.org",
]


class CreateProviderUrls:
    def __init__(self, app_config: AppConfig, release_data: ReleaseInfo, language_data: dict[str, Any]) -> None:
        self.app_config = app_config
        self.release_data = release_data
        self.language_data = language_data
        self.current_language_data: Language = Language(**language_data[app_config.selected_language])

    def retrieve_urls(self) -> ProviderUrls:
        urls = ProviderUrls(
            opensubtitles=self.opensubtitles,
            opensubtitles_hash=self.opensubtitles_hash,
            yifysubtitles=self.yifysubtitles,
            subsource=self.subsource,
        )
        return urls

    @classmethod
    def no_urls(cls) -> ProviderUrls:
        return ProviderUrls([], [], [], [])

    @property
    def subsource(self) -> list[str]:
        return ["https://api.subsource.net/api"]

    @property
    def opensubtitles(self) -> list[str]:
        domain = "https://www.opensubtitles.org"
        subtitle_type = self._opensubtitles_subtitle_type()
        search_parameter = self._opensubtitles_search_parameter()
        return [f"{domain}/{subtitle_type}/{search_parameter}/rss_2_00".replace(" ", "%20")]

    @property
    def opensubtitles_hash(self) -> list[str]:
        domain = "https://www.opensubtitles.org"
        subtitle_type = self._opensubtitles_subtitle_type()
        return [f"{domain}/{subtitle_type}/moviehash-{VIDEO_FILE.file_hash}"]

    @property
    def yifysubtitles(self) -> list[str]:
        if self.release_data.tvseries or not self.release_data.imdb_id:
            return []
        return [f"{mirror}/movie-imdb/{self.release_data.imdb_id}" for mirror in _YIFY_MIRRORS]

    def _opensubtitles_subtitle_type(self) -> str:
        three_letter_code = self.current_language_data.three_letter_code
        hearing_imparied, hearing_imparied_foreign_parts, foreign_parts = self.subtitle_type_logic()
        if hearing_imparied:
            return f"en/search/sublanguageid-{three_letter_code}/hearingimpaired-on"
        elif foreign_parts:
            return f"en/search/sublanguageid-{three_letter_code}/foreignpartsonly-on"
        elif hearing_imparied_foreign_parts:
            return f"en/search/sublanguageid-{three_letter_code}/hearingimpaired-on/foreignpartsonly-on"
        else:
            return f"en/search/sublanguageid-{three_letter_code}"

    def _opensubtitles_search_parameter(self) -> str:
        if self.release_data.tvseries:
            return f"searchonlytvseries-on/season-{self.release_data.season}/episode-{self.release_data.episode}/moviename-{self.release_data.title}"
        return f"searchonlymovies-on/moviename-{self.release_data.title} ({self.release_data.year})"

    def subtitle_type_logic(self) -> tuple[bool, bool, bool]:
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


def get_release_data(filename: str) -> ReleaseInfo:
    if not filename:
        return no_release_data()
    release = filename.lower()
    year = find_year(release)
    season_episode = find_season_episode(release)
    season, season_ordinal, episode, episode_ordinal, series = convert_to_ordinal_string(season_episode)

    title = find_title(release, year, series)
    group = find_group(release)
    imdb_id = ""

    parameters = ReleaseInfo(
        title,
        year,
        season,
        season_ordinal,
        episode,
        episode_ordinal,
        series,
        release,
        group,
        imdb_id,
    )
    return parameters


def no_release_data() -> ReleaseInfo:
    return ReleaseInfo("", 0, "", "", "", "", False, "", "", "")


_STRIPPED_TOKENS: frozenset[str] = frozenset(
    [
        "720p", "1080p", "1440p", "2160p", "4k", "2k",
        "h264", "h265", "x264", "x265", "hevc", "avc",
        "mkv", "mp4", "avi",
    ]
)

_SOURCE_TOKENS: frozenset[str] = frozenset(
    ["web", "webrip", "webdl", "bluray", "bdrip", "hdtv", "dvdrip", "hdrip"]
)

_YEAR_PATTERN: re.Pattern[str] = re.compile(r"^\d{4}$")
_SEASON_EPISODE_PATTERN: re.Pattern[str] = re.compile(r"^s\d+e\d+$")


def _normalize_tokens(filename: str) -> dict:
    group = filename.rsplit("-", 1)[-1].lower()
    raw_tokens = re.split(r"[.\-]", filename.lower())
    year: str | None = None
    season_episode: str | None = None
    source: str | None = None
    title: list[str] = []

    for token in raw_tokens:
        if token in _STRIPPED_TOKENS:
            continue
        if _YEAR_PATTERN.match(token):
            year = token
            continue
        if _SEASON_EPISODE_PATTERN.match(token):
            season_episode = token
            continue
        if token in _SOURCE_TOKENS:
            source = token
            continue
        title.append(token)

    return {"title": title, "year": year, "season_episode": season_episode, "group": group, "source": source}


def calculate_match(from_user: str, from_website: str) -> int:
    tokens_a = _normalize_tokens(from_user)
    tokens_b = _normalize_tokens(from_website)

    if tokens_a == tokens_b:
        return 100

    title_score = round(SequenceMatcher(None, tokens_a["title"], tokens_b["title"]).ratio() * 100)
    group_score = 100 if tokens_a["group"] == tokens_b["group"] else 0
    source_score = 100 if tokens_a["source"] == tokens_b["source"] else 0
    base = (title_score * 60 + group_score * 30 + source_score * 10) // 100

    multiplier = 1.0
    if tokens_a["year"] is not None and tokens_b["year"] is not None and tokens_a["year"] != tokens_b["year"]:
        multiplier *= 0.1
    if (
        tokens_a["season_episode"] is not None
        and tokens_b["season_episode"] is not None
        and tokens_a["season_episode"] != tokens_b["season_episode"]
    ):
        multiplier *= 0.1

    return round(base * multiplier)


def valid_filename(input_string) -> bool:
    forbidden_characters_pattern = r'[<>:"/\\|?*\x00]'
    return bool(re.search(forbidden_characters_pattern, input_string))


def fix_filename(input_string) -> str:
    forbidden_characters_pattern = r'[<>:"/\\|?*\x00]'
    return re.sub(forbidden_characters_pattern, ".", input_string)


def valid_path(input_str, path_resolution) -> bool:
    if input_str == "":
        return False
    patterns = {
        "relative": r"^\.{1,2}\\([a-z0-9-_]|\\[a-z0-9-_])+$|^\.{1,2}$",
        "absolute": r"^[a-zA-Z]{1}:\\([a-z0-9-_]|\\[a-z0-9-_])+$",
    }
    pattern = patterns.get(path_resolution)
    if pattern is None:
        return False
    if not re.match(pattern, input_str):
        return False
    if path_resolution == "absolute":
        return drive_exists(input_str)
    return True


def drive_exists(input_str: str) -> bool:
    return Path(f"{input_str[0]}:\\").exists()


def detect_path_resolution(input_str: str) -> str:
    return "absolute" if re.match(r"^[a-zA-Z]:\\", input_str) else "relative"


def valid_api_request_input(input: str) -> bool:
    pattern = r"^\d+$"
    return bool(re.match(pattern, input))


def valid_subsource_api_key(api_key: str) -> bool:
    pattern = r"^sk_[0-9a-f]+$"
    return bool(re.match(pattern, api_key))
