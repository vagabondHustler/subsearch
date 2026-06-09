import threading
from collections.abc import Callable
from typing import Any

from subsearch.parsing import release_parser
from subsearch.runtime.config.constants import VIDEO_FILE
from subsearch.runtime.logging.logger import log
from subsearch.runtime.models.model import (
    AppConfig,
    Language,
    ProviderDiagnosticStatus,
    ProviderResult,
    ProviderUrls,
    ReleaseInfo,
    Subtitle,
    SubtitleStatus,
)

_subtitle_list_lock = threading.Lock()


def combine_provider_diagnostic_status(*statuses: ProviderDiagnosticStatus) -> ProviderDiagnosticStatus:
    if ProviderDiagnosticStatus.STRUCTURE_INVALID in statuses:
        return ProviderDiagnosticStatus.STRUCTURE_INVALID
    if all(status is ProviderDiagnosticStatus.NO_RESPONSE for status in statuses):
        return ProviderDiagnosticStatus.NO_RESPONSE
    return ProviderDiagnosticStatus.OK


class ProviderDataContainer:
    def __init__(
        self,
        *,
        release_data: ReleaseInfo,
        app_config: AppConfig,
        provider_urls: ProviderUrls,
        language_data: Language,
    ) -> None:
        self.app_config = app_config
        self.release_data = release_data
        self.provider_urls = provider_urls
        self.language_data = language_data

        self.title = release_data.title
        self.year = release_data.year
        self.season = release_data.season
        self.season_ordinal = release_data.season_ordinal
        self.episode = release_data.episode
        self.episode_ordinal = release_data.episode_ordinal
        self.tvseries = release_data.tvseries
        self.release = release_data.release
        self.group = release_data.group
        self.imdb_id = release_data.imdb_id

        self.selected_language = app_config.selected_language
        self.hearing_impaired = app_config.hearing_impaired
        self.non_hearing_impaired = app_config.non_hearing_impaired
        self.accept_threshold = app_config.accept_threshold
        self.open_on_no_matches = app_config.open_manager_on_no_matches
        self.api_call_limit = app_config.api_call_limit
        self.request_connect_timeout = app_config.request_connect_timeout
        self.request_read_timeout = app_config.request_read_timeout
        self.request_timeout = (self.request_connect_timeout, self.request_read_timeout)

        self.url_opensubtitles = provider_urls.opensubtitles
        self.url_opensubtitles_hash = provider_urls.opensubtitles_hash
        self.url_yifysubtitles = provider_urls.yifysubtitles
        self.url_subsource = provider_urls.subsource

        self.file_hash = VIDEO_FILE.file_hash
        self.season_no_padding = release_parser.remove_padded_zero(release_data.season)
        self.episode_no_padding = release_parser.remove_padded_zero(release_data.episode)
        self.ok_season_episode_pattern = self._build_season_episode_patterns()

    def _build_season_episode_patterns(self) -> list[str]:
        padded = [
            f"season.{self.season}.",
            f"s{self.season}e{self.episode}.",
            f"s{self.season}.e{self.episode}.",
        ]
        unpadded = [
            f"season.{self.season_no_padding}.",
            f"s{self.season_no_padding}.e{self.episode_no_padding}.",
        ]
        return padded + unpadded


class SubtitleCollector:
    _accepted: list[Subtitle] = []
    _rejected: list[Subtitle] = []
    _filtered: list[Subtitle] = []

    def __init__(
        self,
        provider_name: str,
        subtitle_name: str,
        download_url: str,
        request_data: dict[str, Any],
        download_headers: dict[str, str],
        hash_match: bool,
        accept_threshold: int,
        token_weights: dict[str, Any],
        token_multipliers: dict[str, Any],
    ) -> None:
        self.provider_name = provider_name
        self.subtitle_name = subtitle_name
        self.download_url = download_url
        self.request_data = request_data
        self.download_headers = download_headers
        self.hash_match = hash_match
        self.accept_threshold = accept_threshold
        self.token_weights = token_weights
        self.token_multipliers = token_multipliers
        self.token_score = 0

    def collect(self, score_override: int | None = None) -> None:
        self._set_token_score(score_override)
        self._add_to_subtitle_list()

    def _set_token_score(self, score_override: int | None) -> None:
        if score_override is not None:
            self.token_score = score_override
        else:
            self.token_score = release_parser.score_subtitle_tokens(
                VIDEO_FILE.filename,
                self.subtitle_name,
                self.token_weights,
                self.token_multipliers,
            )

    def _add_to_subtitle_list(self) -> None:
        subtitle = self._build_subtitle()
        with _subtitle_list_lock:
            if subtitle.status is SubtitleStatus.ACCEPTED:
                log.event(
                    "subtitle_match",
                    provider=self.provider_name,
                    subtitle_name=self.subtitle_name,
                    percentage=self.token_score,
                )
                SubtitleCollector._accepted.append(subtitle)
            else:
                log.event(
                    "subtitle_rejected",
                    provider=self.provider_name,
                    subtitle_name=self.subtitle_name,
                    percentage=self.token_score,
                )
                SubtitleCollector._rejected.append(subtitle)

    def _build_subtitle(self) -> Subtitle:
        sanitized_name = _sanitize_subtitle_filename(self.subtitle_name)
        status = SubtitleStatus.ACCEPTED if self.token_score >= self.accept_threshold else SubtitleStatus.BELOW_THRESHOLD
        if self.download_url:
            return Subtitle(
                token_result=self.token_score,
                provider_name=self.provider_name,
                subtitle_name=sanitized_name.lower(),
                download_url=self.download_url,
                request_data={},
                download_headers=self.download_headers,
                status=status,
                hash_match=self.hash_match,
            )
        if self.request_data:
            return Subtitle(
                token_result=self.token_score,
                provider_name=self.provider_name,
                subtitle_name=sanitized_name.lower(),
                download_url="",
                request_data=self.request_data,
                status=status,
                hash_match=self.hash_match,
            )
        raise ValueError(f"Subtitle has neither download_url nor request_data: {self.subtitle_name!r}")


def _sanitize_subtitle_filename(filename: str) -> str:
    invalid_chars = '<>:"/\\|?*'
    sanitized = filename
    for char in invalid_chars:
        sanitized = sanitized.replace(char, "_")
    sanitized = sanitized.replace("'", "")
    if sanitized != filename:
        log.info(f"Filename sanitized: {filename!r} -> {sanitized!r}")
    return sanitized


class ProviderHelper(ProviderDataContainer):

    def __init__(self, **kwargs) -> None:
        ProviderDataContainer.__init__(self, **kwargs)
        self.provider_name = ""
        self.reported_health: list[ProviderResult] = []
        self.skip_counts: dict[str, int] = {}

    def prepare_subtitle(
        self,
        provider_name: str,
        subtitle_name: str,
        download_url: str,
        request_data: dict[str, Any],
        download_headers: dict[str, str] | None = None,
        percentage_override: int | None = None,
        hash_match: bool = False,
    ) -> None:
        collector = SubtitleCollector(
            provider_name=provider_name,
            subtitle_name=subtitle_name,
            download_url=download_url,
            request_data=request_data,
            download_headers=download_headers or {},
            hash_match=hash_match,
            accept_threshold=self.accept_threshold,
            token_weights=self.app_config.token_weights,
            token_multipliers=self.app_config.token_multipliers,
        )
        collector.collect(percentage_override)

    def record_filtered_out(self, provider_name: str, subtitle_name: str, reason: str) -> None:
        subtitle = Subtitle(
            token_result=0,
            provider_name=provider_name,
            subtitle_name=subtitle_name.lower(),
            download_url="",
            request_data={},
            status=SubtitleStatus.FILTERED_OUT,
        )
        with _subtitle_list_lock:
            SubtitleCollector._filtered.append(subtitle)
            self.skip_counts[reason] = self.skip_counts.get(reason, 0) + 1

    def report_diagnostic_status(self, diagnostic_status: ProviderDiagnosticStatus, subtitles_found: int) -> None:
        result = ProviderResult(self.provider_name, diagnostic_status, subtitles_found)
        self.reported_health.append(result)

    def log_provider_skips(self) -> None:
        total = sum(self.skip_counts.values())
        if not total:
            return
        breakdown = ", ".join(f"{reason}: {count}" for reason, count in self.skip_counts.items())
        log.event("provider_skips", provider=self.provider_name, total=total, breakdown=breakdown)

    def start_search(self, *args, **kwargs) -> None:
        raise NotImplementedError

    def run_search(self, search_fn: Callable[[], ProviderDiagnosticStatus]) -> None:
        subtitles_before = len(self.accepted_subtitles) + len(self.rejected_subtitles)
        try:
            diagnostic_status = search_fn()
        except Exception as error:
            log.error(f"{self.provider_name} response was unrecognized: {error}")
            self.report_diagnostic_status(ProviderDiagnosticStatus.STRUCTURE_INVALID, 0)
            return
        subtitles_after = len(self.accepted_subtitles) + len(self.rejected_subtitles)
        self.log_provider_skips()
        self.report_diagnostic_status(diagnostic_status, subtitles_after - subtitles_before)

    @property
    def accepted_subtitles(self) -> list[Subtitle]:
        with _subtitle_list_lock:
            return SubtitleCollector._accepted

    @property
    def rejected_subtitles(self) -> list[Subtitle]:
        with _subtitle_list_lock:
            return SubtitleCollector._rejected

    @property
    def filtered_subtitles(self) -> list[Subtitle]:
        with _subtitle_list_lock:
            return SubtitleCollector._filtered

    def subtitle_hi_match(self, hearing_impaired: bool) -> bool:
        if self.hearing_impaired and self.non_hearing_impaired:
            return True
        if not self.hearing_impaired and hearing_impaired:
            return False
        if not self.non_hearing_impaired and hearing_impaired:
            return False
        return True

    def subtitle_language_match(self, language: str) -> bool:
        return self.selected_language.lower() == language.lower()

    def keys_exist(self, dictionary: dict[str, Any], keys: list[str]) -> bool:
        return all(key in dictionary for key in keys)

    def threshold_met(self, token_score: int) -> bool:
        return token_score >= self.accept_threshold
