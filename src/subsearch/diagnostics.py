import sys
from datetime import date

from subsearch.io import toml_file
from subsearch.parsing import imdb_lookup, release_parser
from subsearch.providers import opensubtitles, subsource, yifysubtitles
from subsearch.runtime.constants import DEFAULT_CONFIG, FILE_PATHS
from subsearch.runtime.exceptions import MissingApiKey
from subsearch.runtime.logger import log
from subsearch.runtime.model import AppConfig, ProviderHealth, ProviderResult

KNOWN_GOOD_RELEASE = "The.Matrix.1999.1080p.BluRay.x264-GROUP.mkv"

PROVIDER_CLASSES = {
    "opensubtitles": opensubtitles.OpenSubtitles,
    "yifisubtitles": yifysubtitles.YifiSubtitles,
    "subsource": subsource.Subsource,
}


def record_provider_attempt(provider_name: str) -> None:
    _write_provider_date(provider_name, "last_attempt")


def record_provider_known_good(provider_name: str) -> None:
    _write_provider_date(provider_name, "last_known_good")


def _write_provider_date(provider_name: str, field: str) -> None:
    session = toml_file.get_config_session()
    session.write(f"diagnostics.provider_health.{provider_name}.{field}", date.today().isoformat())
    session.commit()


def record_health_reports(reports: list[ProviderResult]) -> None:
    if not FILE_PATHS.config.exists():
        return None
    for report in reports:
        record_provider_attempt(report.provider_name)
        if report.health is ProviderHealth.OK and report.subtitles_found > 0:
            record_provider_known_good(report.provider_name)


def providers_due_for_diagnostic(app_config: AppConfig) -> list[str]:
    interval_days = app_config.diagnostics["interval_days"]
    provider_health = app_config.diagnostics["provider_health"]
    due = []
    for provider_name, dates in provider_health.items():
        if _days_between(dates["last_known_good"], dates["last_attempt"]) >= interval_days:
            due.append(provider_name)
    return due


def _days_between(earlier: str, later: str) -> int:
    if not later:
        return 0

    later_date = date.fromisoformat(later)
    earlier_date = date.fromisoformat(earlier) if earlier else date.min

    return (later_date - earlier_date).days


def diagnose_providers(provider_names: list[str]) -> list[ProviderResult]:
    search_kwargs = _known_good_search_kwargs()
    reports = [_diagnose_imdb(search_kwargs)] if "imdb" in provider_names else []
    for provider_name in provider_names:
        provider_class = PROVIDER_CLASSES.get(provider_name)
        if provider_class is None:
            continue
        provider = provider_class(**search_kwargs)
        try:
            provider.start_search(flag="site")
        except MissingApiKey:
            pass
        reports.extend(provider.reported_health)
    return reports


def _load_app_config() -> AppConfig:
    if not FILE_PATHS.config.exists():
        return toml_file.get_app_config_from_data(DEFAULT_CONFIG)
    toml_file.resolve_on_integrity_failure()
    toml_file.reset_config_session()
    return toml_file.get_config_session().snapshot()


def _diagnose_imdb(search_kwargs: dict) -> ProviderResult:
    release_data = search_kwargs["release_data"]
    lookup = imdb_lookup.ImdbIdLookup(release_data.title, release_data.year, release_data.tvseries)
    return ProviderResult("imdb", lookup.health, 1 if lookup.imdb_id else 0)


def _known_good_search_kwargs() -> dict:
    app_config = _load_app_config()
    language_data = toml_file.load_toml_data(FILE_PATHS.subtitle_languages)
    release_data = release_parser.get_release_data(KNOWN_GOOD_RELEASE)
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
    return report.health is not ProviderHealth.OK or report.subtitles_found == 0


def run_all_providers() -> list[ProviderResult]:
    return diagnose_providers(["imdb", *PROVIDER_CLASSES.keys()])


def main() -> int:
    reports = run_all_providers()
    unhealthy = [report for report in reports if _provider_is_unhealthy(report)]
    for report in reports:
        status = "unhealthy" if _provider_is_unhealthy(report) else "healthy"
        log.stdout(f"{report.provider_name}: {status} ({report.health.value}, found {report.subtitles_found})")
    return 1 if unhealthy else 0


if __name__ == "__main__":
    sys.exit(main())
