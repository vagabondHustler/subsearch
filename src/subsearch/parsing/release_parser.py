import re
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, NamedTuple

from subsearch.runtime.config.defaults import (
    DEFAULT_TOKEN_MULTIPLIERS,
    DEFAULT_TOKEN_WEIGHTS,
)
from subsearch.runtime.models import (
    AppConfig,
    Language,
    MatchTier,
    ProviderUrls,
    ReleaseInfo,
    classify_match_tier,
)
from subsearch.runtime.recorder import LogLevel, capture


def remove_padded_zero(x: str) -> str:
    lenght = len(x)
    if x.startswith("0") and lenght > 1:
        return str(x)[1:]
    return x


# matches a 4-digit year (1000–2999) preceded by a dot/space/hyphen/"(" and followed by one or end of string,
# so it works for release names ("Movie.Title.2023.1080p") and typed terms ("the matrix 1999", "the matrix (1999)")
_RELEASE_YEAR_PATTERN = re.compile(r"(?<=[. (\-])([1-2][0-9]{3})(?=[. )\-]|$)")
# matches a season/episode token in the forms s01e02, s01.e02, s01 e02 or s01-e02, at a token boundary
_RELEASE_SEASON_EPISODE_PATTERN = re.compile(r"(?:^|[. (\-])s(\d{1,2})[. \-]?e(\d{1,4})(?=[. )\-]|$)")
# matches a lone season token (s01) with no episode following, at a token boundary e.g. "breaking bad s01"
_PARTIAL_SEASON_PATTERN = re.compile(r"(?:^|[. (\-])s(\d{1,2})(?=[. )\-]|$)")
# matches a lone episode token (e01) with no season preceding, at a token boundary e.g. "breaking bad e01"
_PARTIAL_EPISODE_PATTERN = re.compile(r"(?:^|[. (\-])e(\d{1,4})(?=[. )\-]|$)")
# matches the NxNN season/episode form e.g. 1x03 or [1x14], at a token boundary
_RELEASE_SEASON_EPISODE_X_PATTERN = re.compile(r"(?:^|[. (\[\-])(\d{1,2})x(\d{1,4})(?=[. )\]\-]|$)")
# matches punctuation users type freely but release names omit: apostrophes, backticks, colons, semicolons, commas, quotes, ! and ?
_TYPED_PUNCTUATION_PATTERN = re.compile(r"[’'`:;,!?\"]")


def normalize_typed_punctuation(string: str) -> str:
    without_punctuation = _TYPED_PUNCTUATION_PATTERN.sub("", string.replace("&", " and "))
    return " ".join(without_punctuation.split())


def _looks_like_typed_term(string: str) -> bool:
    return "." not in string


def find_year(string: str) -> int:
    years = _RELEASE_YEAR_PATTERN.findall(string)
    if years:
        return int(years[-1])
    return 0


def _title_before(string: str, cutoff: int) -> str:
    return " ".join(string[:cutoff].replace(".", " ").split()).strip(" (-")


def find_title_by_year(string: str) -> str:
    year_matches = list(_RELEASE_YEAR_PATTERN.finditer(string))
    if year_matches:
        return _title_before(string, year_matches[-1].start())
    return ""


def find_title_by_show(string: str) -> str:
    season_episode_match = _RELEASE_SEASON_EPISODE_PATTERN.search(string)
    if season_episode_match:
        return _title_before(string, season_episode_match.start())
    return ""


def find_season_episode(string: str) -> str:
    season_episode_match = _RELEASE_SEASON_EPISODE_PATTERN.search(string)
    if season_episode_match:
        return f"s{season_episode_match.group(1)}e{season_episode_match.group(2)}"
    return ""


class PartialSeasonEpisode(NamedTuple):
    season: int
    episode: int


def find_partial_season_episode(typed_term: str) -> PartialSeasonEpisode:
    normalized = normalize_typed_punctuation(typed_term.lower())
    if _RELEASE_SEASON_EPISODE_PATTERN.search(normalized):
        return PartialSeasonEpisode(0, 0)
    season_match = _PARTIAL_SEASON_PATTERN.search(normalized)
    episode_match = _PARTIAL_EPISODE_PATTERN.search(normalized)
    season = int(season_match.group(1)) if season_match else 0
    episode = int(episode_match.group(1)) if episode_match else 0
    return PartialSeasonEpisode(season, episode)


def convert_to_ordinal_string(string: str) -> tuple[str, str, str, str, bool]:
    if string == "":
        season, season_ordinal, episode, episode_ordinal = "", "", "", ""
        show_bool = False
    else:
        from num2words import num2words

        season, episode = string.replace("s", "").replace("e", " ").split(" ")
        season_ordinal = num2words(int(season), lang="en", to="ordinal")
        episode_ordinal = num2words(int(episode), lang="en", to="ordinal")
        show_bool = True
    return season, season_ordinal, episode, episode_ordinal, show_bool


def find_group(string: str) -> str:
    group = string.rsplit("-", 1)[-1]
    return group


def _typed_term_title(string: str) -> str:
    return " ".join(_normalize_tokens(string)["title"])


def find_title(filename: str, year: int, series: bool) -> str:
    if year != 0:
        title = find_title_by_year(filename)
    elif series and year == 0:
        title = find_title_by_show(filename)
    elif _looks_like_typed_term(filename):
        title = _typed_term_title(filename)
    else:
        title = filename.rsplit("-", 1)[0]
    return title


_YIFYSUBTITLES_MIRRORS: list[str] = [
    "https://yifysubtitles.ch",
    "https://yifysubtitles.mx",
    "https://yifysubtitles.org",
]


class CreateProviderUrls:
    def __init__(
        self, app_config: AppConfig, release_data: ReleaseInfo, language_data: dict[str, Any], file_hash: str = ""
    ) -> None:
        self.app_config = app_config
        self.release_data = release_data
        self.language_data = language_data
        self.file_hash = file_hash
        self.current_language_data: Language = Language(**language_data[app_config.selected_language])

    def retrieve_urls(self) -> ProviderUrls:
        urls = ProviderUrls(
            opensubtitles=self.opensubtitles,
            opensubtitles_hash=self.opensubtitles_hash,
            yifysubtitles=self.yifysubtitles,
            subsource=self.subsource,
            tvsubtitles=self.tvsubtitles,
        )
        return urls

    @classmethod
    def no_urls(cls) -> ProviderUrls:
        return ProviderUrls([], [], [], [], [])

    @property
    def subsource(self) -> list[str]:
        return ["https://api.subsource.net/api"]

    @property
    def tvsubtitles(self) -> list[str]:
        if not self.release_data.tvseries:
            return []
        return ["https://www.tvsubtitles.net"]

    @property
    def opensubtitles(self) -> list[str]:
        domain = "https://www.opensubtitles.org"
        subtitle_type = self._opensubtitles_subtitle_type()
        search_parameter = self._opensubtitles_search_parameter()
        return [f"{domain}/{subtitle_type}/{search_parameter}/rss_2_00".replace(" ", "%20")]

    @property
    def opensubtitles_hash(self) -> list[str]:
        if not self.file_hash:
            return []
        domain = "https://www.opensubtitles.org"
        subtitle_type = self._opensubtitles_subtitle_type()
        return [f"{domain}/{subtitle_type}/moviehash-{self.file_hash}"]

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
        if self.release_data.year == 0:
            # typed term without a year: movie/series unknown, so search everything and skip the year suffix
            return f"moviename-{self.release_data.title}"
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
    release = normalize_typed_punctuation(filename.lower())
    year = find_year(release)
    season_episode = find_season_episode(release)
    season, season_ordinal, episode, episode_ordinal, series = convert_to_ordinal_string(season_episode)

    title = find_title(release, year, series)
    group = "" if _looks_like_typed_term(release) else find_group(release)
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


def _canonical_season_episode(season: str, episode: str) -> str:
    return f".s{int(season):02d}e{int(episode):02d}"


def _collapse_season_episode(filename: str) -> str:
    collapsed = _RELEASE_SEASON_EPISODE_PATTERN.sub(
        lambda match: _canonical_season_episode(match.group(1), match.group(2)), filename
    )
    return _RELEASE_SEASON_EPISODE_X_PATTERN.sub(
        lambda match: _canonical_season_episode(match.group(1), match.group(2)), collapsed
    )


def _normalize_tokens(filename: str) -> dict:
    lowered = _collapse_season_episode(normalize_typed_punctuation(filename.lower()))
    has_release_group = "-" in lowered and not _looks_like_typed_term(lowered)
    group = lowered.rsplit("-", 1)[-1] if has_release_group else ""
    # dots, spaces, hyphens, or square/round brackets as delimiters
    raw_tokens = [token for token in re.split(r"[. \-\[\]()]", lowered) if token]
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

    if group and title and title[-1] == group:
        title.pop()

    return {
        "title": title,
        "year": year,
        "season_episode": season_episode,
        "group": group,
        "source": source,
        "edition": edition,
    }


def _fields_conflict(value_a: Any, value_b: Any) -> bool:
    return bool(value_a) and bool(value_b) and value_a != value_b


def _mismatch_factor(tokens_a: dict, tokens_b: dict, multipliers: dict[str, float]) -> float:
    multiplier = 1.0
    year_a, year_b = tokens_a["year"], tokens_b["year"]
    if _fields_conflict(year_a, year_b):
        multiplier *= multipliers["year"]
    if _fields_conflict(tokens_a["season_episode"], tokens_b["season_episode"]):
        multiplier *= multipliers["season_episode"]
    if _fields_conflict(tokens_a["edition"], tokens_b["edition"]):
        multiplier *= multipliers["edition"]
    return multiplier


# below this ratio two words are considered different words rather than a typo of the same word
_TOKEN_SIMILARITY_CUTOFF = 0.75


def _token_similarity(token_a: str, token_b: str) -> float:
    return SequenceMatcher(None, token_a, token_b).ratio()


def _fuzzy_title_score(title_a: list[str], title_b: list[str]) -> int:
    if not title_a and not title_b:
        return 100
    unmatched = list(title_b)
    matched_similarity_sum = 0.0
    for token in title_a:
        if not unmatched:
            break
        best_candidate = max(unmatched, key=lambda candidate: _token_similarity(token, candidate))
        similarity = _token_similarity(token, best_candidate)
        if similarity >= _TOKEN_SIMILARITY_CUTOFF:
            matched_similarity_sum += similarity
            unmatched.remove(best_candidate)
    return round(2 * matched_similarity_sum / (len(title_a) + len(title_b)) * 100)


def _group_score(group_a: str, group_b: str) -> int:
    if group_a == group_b:
        return 100
    if not group_a or not group_b:
        return 50
    return 0


def _get_base_score(tokens_a: dict, tokens_b: dict, weights: dict[str, float]) -> int:
    title_score = _fuzzy_title_score(tokens_a["title"], tokens_b["title"])
    group_score = _group_score(tokens_a["group"], tokens_b["group"])
    source_score = round(_source_compatibility(tokens_a["source"], tokens_b["source"]) * 100)
    weighted_total = title_score * weights["title"] + group_score * weights["group"] + source_score * weights["source"]
    return int(weighted_total // 100)


def score_subtitle_tokens(
    reference: str,
    from_provider: str,
    token_weights: dict[str, float] = DEFAULT_TOKEN_WEIGHTS,
    token_multipliers: dict[str, float] = DEFAULT_TOKEN_MULTIPLIERS,
    log_match: bool = True,
) -> int:
    reference_tokens = _normalize_tokens(reference)
    provider_tokens = _normalize_tokens(from_provider)

    if reference_tokens == provider_tokens:
        if log_match:
            capture(f"Fuzzy match: exact token match for {from_provider!r}", level=LogLevel.DEBUG)
        return 100

    base_score = _get_base_score(reference_tokens, provider_tokens, token_weights)
    mismatch_multiplier = _mismatch_factor(reference_tokens, provider_tokens, token_multipliers)
    score = round(base_score * mismatch_multiplier)

    if log_match:
        capture(
            f"Fuzzy match: {score}% for {from_provider!r} " f"(base {base_score}, mismatch ×{mismatch_multiplier:.2f})",
            level=LogLevel.DEBUG,
        )
    return score


_HASH_MATCH_PREFIX = "hashmatch__"


def rank_best_subtitle(
    files: list[Path],
    release_name: str,
    token_weights: dict[str, float],
    token_multipliers: dict[str, float],
    accept_threshold: int,
) -> Path:
    best_rank: tuple[MatchTier, int] = (MatchTier.C, 0)
    best_match = Path(".")
    for file in files:
        is_hash_match = file.name.startswith(_HASH_MATCH_PREFIX)
        token_name = file.name.removeprefix(_HASH_MATCH_PREFIX)
        token_score = score_subtitle_tokens(token_name, release_name, token_weights, token_multipliers)
        tier = classify_match_tier(is_hash_match, token_score, accept_threshold)
        rank = (tier, token_score)
        if rank > best_rank:
            best_rank = rank
            best_match = file
    return best_match


def valid_filename(input_string: str) -> bool:
    # matches any Windows-forbidden filename character: < > : " / \ | ? * or null byte
    forbidden_characters_pattern = r'[<>:"/\\|?*\x00]'
    return bool(re.search(forbidden_characters_pattern, input_string))


def fix_filename(input_string: str) -> str:
    # replaces any Windows-forbidden filename character with a dot
    forbidden_characters_pattern = r'[<>:"/\\|?*\x00]'
    return re.sub(forbidden_characters_pattern, ".", input_string)


def valid_path(input_str: str, path_resolution: str) -> bool:
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
