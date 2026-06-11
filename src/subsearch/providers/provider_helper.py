import threading
from collections.abc import Callable
from typing import Any

from subsearch.parsing import release_parser
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


def combine_provider_diagnostic_status(*statuses: ProviderDiagnosticStatus) -> ProviderDiagnosticStatus:
    if ProviderDiagnosticStatus.STRUCTURE_INVALID in statuses:
        return ProviderDiagnosticStatus.STRUCTURE_INVALID
    if all(status is ProviderDiagnosticStatus.NO_RESPONSE for status in statuses):
        return ProviderDiagnosticStatus.NO_RESPONSE
    return ProviderDiagnosticStatus.OK


class SubtitleResults:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._seen: set[tuple[str, str, str]] = set()
        self.accepted: list[Subtitle] = []
        self.rejected: list[Subtitle] = []
        self.filtered: list[Subtitle] = []

    def add(self, subtitle: Subtitle) -> bool:
        identity = (subtitle.provider_name, subtitle.subtitle_name, subtitle.download_url)
        with self._lock:
            if identity in self._seen:
                return False
            self._seen.add(identity)
            if subtitle.status is SubtitleStatus.ACCEPTED:
                self.accepted.append(subtitle)
            elif subtitle.status is SubtitleStatus.FILTERED_OUT:
                self.filtered.append(subtitle)
            else:
                self.rejected.append(subtitle)
            return True


def _sanitize_subtitle_filename(filename: str) -> str:
    invalid_chars = '<>:"/\\|?*'
    sanitized = filename
    for char in invalid_chars:
        sanitized = sanitized.replace(char, "_")
    sanitized = sanitized.replace("'", "")
    if sanitized != filename:
        log.debug(f"Filename sanitized: {filename!r} -> {sanitized!r}")
    return sanitized


class ProviderHelper:
    def __init__(
        self,
        *,
        release_data: ReleaseInfo,
        app_config: AppConfig,
        provider_urls: ProviderUrls,
        language_data: Language,
        filename: str,
        subtitle_results: SubtitleResults | None = None,
    ) -> None:
        self.release_data = release_data
        self.app_config = app_config
        self.provider_urls = provider_urls
        self.language_data = language_data
        self.filename = filename
        self.subtitle_results = subtitle_results or SubtitleResults()

        self.request_timeout = (app_config.request_connect_timeout, app_config.request_read_timeout)
        self.season_no_padding = release_parser.remove_padded_zero(release_data.season)

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
        if percentage_override is not None:
            token_score = percentage_override
        else:
            token_score = release_parser.score_subtitle_tokens(
                self.filename,
                subtitle_name,
                self.app_config.token_weights,
                self.app_config.token_multipliers,
            )
        sanitized_name = _sanitize_subtitle_filename(subtitle_name)
        status = (
            SubtitleStatus.ACCEPTED
            if token_score >= self.app_config.accept_threshold
            else SubtitleStatus.BELOW_THRESHOLD
        )
        if download_url:
            subtitle = Subtitle(
                token_result=token_score,
                provider_name=provider_name,
                subtitle_name=sanitized_name.lower(),
                download_url=download_url,
                request_data={},
                download_headers=download_headers or {},
                status=status,
                hash_match=hash_match,
            )
        elif request_data:
            subtitle = Subtitle(
                token_result=token_score,
                provider_name=provider_name,
                subtitle_name=sanitized_name.lower(),
                download_url="",
                request_data=request_data,
                status=status,
                hash_match=hash_match,
            )
        else:
            raise ValueError(f"Subtitle has neither download_url nor request_data: {subtitle_name!r}")
        if not self.subtitle_results.add(subtitle):
            return
        if status is SubtitleStatus.ACCEPTED:
            log.event(
                "subtitle_match",
                provider=provider_name,
                subtitle_name=subtitle_name,
                percentage=token_score,
            )
        else:
            log.event(
                "subtitle_rejected",
                provider=provider_name,
                subtitle_name=subtitle_name,
                percentage=token_score,
            )

    def record_filtered_out(self, provider_name: str, subtitle_name: str, reason: str) -> None:
        subtitle = Subtitle(
            token_result=0,
            provider_name=provider_name,
            subtitle_name=subtitle_name.lower(),
            download_url="",
            request_data={},
            status=SubtitleStatus.FILTERED_OUT,
        )
        if self.subtitle_results.add(subtitle):
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
        return self.subtitle_results.accepted

    @property
    def rejected_subtitles(self) -> list[Subtitle]:
        return self.subtitle_results.rejected

    @property
    def filtered_subtitles(self) -> list[Subtitle]:
        return self.subtitle_results.filtered

    def subtitle_hi_match(self, hearing_impaired: bool) -> bool:
        if self.app_config.hearing_impaired and self.app_config.non_hearing_impaired:
            return True
        if not self.app_config.hearing_impaired and hearing_impaired:
            return False
        if not self.app_config.non_hearing_impaired and hearing_impaired:
            return False
        return True

    def subtitle_language_match(self, language: str) -> bool:
        return self.app_config.selected_language.lower() == language.lower()

    def keys_exist(self, dictionary: dict[str, Any], keys: list[str]) -> bool:
        return all(key in dictionary for key in keys)
