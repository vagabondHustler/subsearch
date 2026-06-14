import sys

from subsearch.io.language_data import load_language_data
from subsearch.parsing import imdb_lookup, release_parser
from subsearch.providers import opensubtitles, subsource, yifysubtitles
from subsearch.runtime.config import DEFAULT_CONFIG, FILE_PATHS
from subsearch.runtime.config import session as config_session
from subsearch.runtime.logging.logger import log
from subsearch.runtime.models import (
    AppConfig,
    ProviderDiagnosticStatus,
    ProviderResult,
)
from subsearch.runtime.models.exceptions import MissingApiKey

KNOWN_GOOD_RELEASE = "The.Matrix.1999.1080p.BluRay.x264-GROUP.mkv"

PROVIDER_CLASSES = {
    "opensubtitles": opensubtitles.OpenSubtitles,
    "yifysubtitles": yifysubtitles.YifySubtitles,
    "subsource": subsource.Subsource,
}


def record_health_reports(reports: list[ProviderResult]) -> None:
    if not FILE_PATHS.config.exists():
        return None
    session = config_session.get_config_session()
    for report in reports:
        key = f"diagnostics.provider_diagnostics.{report.provider_name}.failed_attempts"
        if report.diagnostic_status is ProviderDiagnosticStatus.OK and report.subtitles_found > 0:
            log.debug(f"{report.provider_name}: healthy , resetting failed_attempts to 0")
            session.write(key, 0)
        else:
            current = session.read(key) or 0
            updated = current + 1
            log.warning(
                f"{report.provider_name}: unhealthy ({report.diagnostic_status.value}, found {report.subtitles_found}) , failed_attempts {current} -> {updated}"
            )
            session.write(key, updated)
    session.commit()


def providers_due_for_diagnostic(app_config: AppConfig) -> list[str]:
    threshold = app_config.diagnostics["failed_attempts_threshold"]
    provider_diagnostics = app_config.diagnostics["provider_diagnostics"]
    due = [
        provider_name
        for provider_name, health in provider_diagnostics.items()
        if health["failed_attempts"] >= threshold
    ]
    if due:
        log.info(f"Providers due for diagnostic (threshold={threshold}): {', '.join(due)}")
    return due


def diagnose_providers(provider_names: list[str]) -> list[ProviderResult]:
    log.info(f"Running diagnostics for: {', '.join(provider_names)}")
    search_kwargs = _known_good_search_kwargs()
    reports = [_diagnose_imdb(search_kwargs)] if "imdb" in provider_names else []
    for provider_name in provider_names:
        provider_class = PROVIDER_CLASSES.get(provider_name)
        if provider_class is None:
            continue
        log.debug(f"Probing {provider_name}")
        provider = provider_class(**search_kwargs)
        try:
            provider.start_search(flag="site")
        except MissingApiKey:
            log.warning(f"{provider_name}: skipped , missing API key")
        reports.extend(provider.reported_health)
    return reports


def _load_app_config() -> AppConfig:
    if not FILE_PATHS.config.exists():
        return config_session.get_app_config_from_data(DEFAULT_CONFIG)
    config_session.reset_config_session()
    return config_session.get_config_session().snapshot()


def _diagnose_imdb(search_kwargs: dict) -> ProviderResult:
    release_data = search_kwargs["release_data"]
    lookup = imdb_lookup.ImdbIdLookup(release_data.title, release_data.year, release_data.tvseries)
    return ProviderResult("imdb", lookup.diagnostic_status, 1 if lookup.imdb_id else 0)


def _known_good_search_kwargs() -> dict:
    app_config = _load_app_config()
    language_data = load_language_data()
    release_data = release_parser.get_release_info(KNOWN_GOOD_RELEASE)
    lookup = imdb_lookup.ImdbIdLookup(release_data.title, release_data.year, release_data.tvseries)
    release_data.imdb_id = lookup.imdb_id
    provider_urls = release_parser.CreateProviderUrls(app_config, release_data, language_data).retrieve_urls()
    return dict(
        release_data=release_data,
        app_config=app_config,
        provider_urls=provider_urls,
        language_data=language_data,
    )


def _provider_is_unhealthy(report: ProviderResult) -> bool:
    return report.diagnostic_status is not ProviderDiagnosticStatus.OK or report.subtitles_found == 0


def run_all_providers() -> list[ProviderResult]:
    return diagnose_providers(["imdb", *PROVIDER_CLASSES.keys()])


def main() -> int:
    reports = run_all_providers()
    unhealthy = [report for report in reports if _provider_is_unhealthy(report)]
    for report in reports:
        status = "unhealthy" if _provider_is_unhealthy(report) else "healthy"
        log.info(f"{report.provider_name}: {status} ({report.diagnostic_status.value}, found {report.subtitles_found})")
    return 1 if unhealthy else 0


if __name__ == "__main__":
    sys.exit(main())
