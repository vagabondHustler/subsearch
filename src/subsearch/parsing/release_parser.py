import re
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

from num2words import num2words

from subsearch.runtime.config.constants import VIDEO_FILE
from subsearch.runtime.config.static_values import (
    DEFAULT_TOKEN_MULTIPLIERS,
    DEFAULT_TOKEN_WEIGHTS,
)
from subsearch.runtime.logging.logger import log
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
    # matches a 4-digit year between dots (1000–2999) e.g. "Movie.Title.2023.1080p" → "2023"
    re_year = re.findall(r"^.*\.([1-2][0-9]{3})\.", string)
    if re_year:
        year = re_year[0]
        return int(year)
    return 0


def find_title_by_year(string: str) -> str:
    # captures everything before the year segment e.g. "Movie.Title.2023.1080p" → "Movie.Title"
    re_title = re.findall(r"^(.*)\.[1-2][0-9]{3}\.", string)
    if re_title:
        title: str = re_title[0]
        title = title.replace(".", " ")
        return title
    return ""


def find_title_by_show(string: str) -> str:
    # captures everything before the SxxExx segment e.g. "Show.Title.S01E02.1080p" → "Show.Title"
    re_title = re.findall(r"^(.*)\.[s]\d*[e]\d*\.", string)
    if re_title:
        title: str = re_title[0]
        title = title.replace(".", " ")
        return title
    return ""


def find_season_episode(string: str) -> str:
    # captures the SxxExx token between dots e.g. "Show.Title.S01E02.1080p" → "S01E02"
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


_YIFYSUBTITLES_MIRRORS: list[str] = [
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
        return [f"{mirror}/movie-imdb/{self.release_data.imdb_id}" for mirror in _YIFYSUBTITLES_MIRRORS]

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


def get_release_info(filename: str) -> ReleaseInfo:
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
        "720p",
        "1080p",
        "1440p",
        "2160p",
        "4k",
        "2k",
        "h264",
        "h265",
        "x264",
        "x265",
        "hevc",
        "avc",
        "av1",
        "vp9",
        "xvid",
        "divx",
        "10bit",
        "8bit",
        "hdr",
        "hdr10",
        "dv",
        "sdr",
        "dts",
        "dtshd",
        "ac3",
        "eac3",
        "dd",
        "ddp",
        "aac",
        "truehd",
        "atmos",
        "flac",
        "mkv",
        "mp4",
        "avi",
        "proper",
        "repack",
    ]
)

_SOURCE_TOKEN_FAMILIES: dict[str, frozenset[str]] = {
    "digital": frozenset(["web", "webrip", "webdl"]),
    "bluray": frozenset(["bluray", "bdrip", "brrip", "remux"]),
    "dvd": frozenset(["dvdrip", "dvdscr"]),
    "broadcast": frozenset(["hdtv", "hdrip"]),
    "cam": frozenset(["cam", "ts", "telesync"]),
}

_SOURCE_TOKENS: frozenset[str] = frozenset().union(*_SOURCE_TOKEN_FAMILIES.values())

_SOURCE_FAMILY_BY_TOKEN: dict[str, str] = {
    token: family for family, tokens in _SOURCE_TOKEN_FAMILIES.items() for token in tokens
}

_SOURCE_COMPATIBILITY: dict[frozenset[str], float] = {
    frozenset(["digital", "bluray"]): 0.5,
    frozenset(["dvd", "broadcast"]): 0.5,
}

_EDITION_TOKENS: frozenset[str] = frozenset(
    [
        "extended",
        "uncut",
        "unrated",
        "remastered",
        "theatrical",
        "imax",
        "directors",
        "cut",
    ]
)

# matches exactly 4 digits e.g. "2023" matches, "20231" does not
_YEAR_PATTERN: re.Pattern[str] = re.compile(r"^\d{4}$")
# matches lowercase SxxExx with one or more digits each e.g. "s01e02" matches, "S01E02" does not
_SEASON_EPISODE_PATTERN: re.Pattern[str] = re.compile(r"^s\d+e\d+$")


def _source_compatibility(source_a: str | None, source_b: str | None) -> float:
    if source_a is None and source_b is None:
        return 1.0
    if source_a is None or source_b is None:
        return 0.5
    family_a = _SOURCE_FAMILY_BY_TOKEN[source_a]
    family_b = _SOURCE_FAMILY_BY_TOKEN[source_b]
    if family_a == "cam" or family_b == "cam":
        return 0.0
    if family_a == family_b:
        return 1.0
    return _SOURCE_COMPATIBILITY.get(frozenset([family_a, family_b]), 0.0)


def _normalize_tokens(filename: str) -> dict:
    group = filename.rsplit("-", 1)[-1].lower()
    raw_tokens = re.split(r"[.\-]", filename.lower())  # dots or hyphens as delimiters
    year: str | None = None
    season_episode: str | None = None
    source: str | None = None
    edition: set[str] = set()
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
        if token in _EDITION_TOKENS:
            edition.add(token)
            continue
        title.append(token)

    return {
        "title": title,
        "year": year,
        "season_episode": season_episode,
        "group": group,
        "source": source,
        "edition": edition,
    }


def _fields_conflict(value_a, value_b) -> bool:
    return bool(value_a) and bool(value_b) and value_a != value_b


def _penalty_to_multiplier(penalty: int) -> float:
    return (100 - penalty) / 100


def _mismatch_factor(tokens_a: dict, tokens_b: dict, multipliers: dict[str, int]) -> float:
    multiplier = 1.0
    year_a, year_b = tokens_a["year"], tokens_b["year"]
    if _fields_conflict(year_a, year_b):
        multiplier *= _penalty_to_multiplier(multipliers["year"])
    if _fields_conflict(tokens_a["season_episode"], tokens_b["season_episode"]):
        multiplier *= _penalty_to_multiplier(multipliers["season_episode"])
    if _fields_conflict(tokens_a["edition"], tokens_b["edition"]):
        multiplier *= _penalty_to_multiplier(multipliers["edition"])
    return multiplier


def _get_base_score(tokens_a: dict, tokens_b: dict, weights: dict[str, float]) -> int:
    title_score = round(SequenceMatcher(None, tokens_a["title"], tokens_b["title"]).ratio() * 100)
    group_score = 100 if tokens_a["group"] == tokens_b["group"] else 0
    source_score = round(_source_compatibility(tokens_a["source"], tokens_b["source"]) * 100)
    return (title_score * weights["title"] + group_score * weights["group"] + source_score * weights["source"]) // 100


def score_subtitle_tokens(
    reference: str,
    from_provider: str,
    token_weights: dict[str, float] = DEFAULT_TOKEN_WEIGHTS,
    token_multipliers: dict[str, int] = DEFAULT_TOKEN_MULTIPLIERS,
) -> int:
    reference_tokens = _normalize_tokens(reference)
    provider_tokens = _normalize_tokens(from_provider)

    if reference_tokens == provider_tokens:
        return 100

    base_score = _get_base_score(reference_tokens, provider_tokens, token_weights)
    mismatch_multiplier = _mismatch_factor(reference_tokens, provider_tokens, token_multipliers)
    score = round(base_score * mismatch_multiplier)

    return score


def valid_filename(input_string) -> bool:
    # matches any Windows-forbidden filename character: < > : " / \ | ? * or null byte
    forbidden_characters_pattern = r'[<>:"/\\|?*\x00]'
    return bool(re.search(forbidden_characters_pattern, input_string))


def fix_filename(input_string) -> str:
    # replaces any Windows-forbidden filename character with a dot
    forbidden_characters_pattern = r'[<>:"/\\|?*\x00]'
    return re.sub(forbidden_characters_pattern, ".", input_string)


def valid_path(input_str, path_resolution) -> bool:
    if input_str == "":
        return False
    patterns = {
        # matches relative Windows paths like ".\folder\sub" or ".." (case-insensitive segments)
        "relative": r"^\.{1,2}\\([a-zA-Z0-9-_]|\\[a-zA-Z0-9-_])+$|^\.{1,2}$",
        # matches absolute Windows paths like "C:\folder\sub" (case-insensitive segments)
        "absolute": r"^[a-zA-Z]{1}:\\([a-zA-Z0-9-_]|\\[a-zA-Z0-9-_])+$",
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
    # matches a Windows drive root like "C:\" to distinguish absolute from relative paths
    return "absolute" if re.match(r"^[a-zA-Z]:\\", input_str) else "relative"


def valid_subsource_api_key(api_key: str) -> bool:
    # matches a subsource API key: "sk_" followed by one or more lowercase hex characters
    pattern = r"^sk_[0-9a-f]+$"
    return bool(re.match(pattern, api_key))
