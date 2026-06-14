import dataclasses
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from subsearch.runtime.models import DataclassInstance


class LogColor:
    BANNER = "#fab387"  # orange — section banners / selections
    MATCH = "#a6e3a1"  # green — accepted subtitle / success
    SUCCESS = "#89b4fa"  # blue — task completed / done
    WARN = "#f9e2af"  # yellow — soft warnings
    FAIL = "#f38ba8"  # red — failures
    FINISH = "#f2cdcd"  # peach — run summary line


@dataclass(frozen=True, slots=True)
class LogEvent:
    template: str
    color: Optional[str] = None
    bold: bool = False
    console: bool = True

    def render(self, **values: Any) -> str:
        return self.template.format(**values)


class FilesystemEvent(LogEvent):
    def render(self, **values: Any) -> str:
        source: Path = values["src"]
        destination: Optional[Path] = values.get("dst")
        return super().render(kind=_path_kind(source), src=_shorten(source), dst=_shorten(destination))


def _path_kind(path: Path) -> str:
    if path.is_file():
        return "file"
    if path.is_dir():
        return "directory"
    return "item"


def _shorten(path: Optional[Path]) -> Optional[Path]:
    if path is None:
        return None
    try:
        return path.relative_to(path.parent.parent)
    except ValueError:
        return path


LOG_EVENTS: dict[str, LogEvent] = {
    "banner": LogEvent("--- [{title}] ---", LogColor.BANNER, bold=True),
    "task_completed": LogEvent("Tasks completed", LogColor.SUCCESS),
    "video_file_selected": LogEvent("Selected video file: {filename}", LogColor.BANNER, bold=True),
    "subtitle_match": LogEvent("{provider:<14}{percentage:>3}% {subtitle_name}", LogColor.MATCH),
    "subtitle_rejected": LogEvent("{provider:<14}{percentage:>3}% {subtitle_name}"),
    "provider_skips": LogEvent("{provider:<14}skipped {total} ({breakdown})"),
    "remove": FilesystemEvent(r"Removing {kind}: ...\{src}", console=False),
    "rename": FilesystemEvent(r"Renaming {kind}: ...\{src} -> ...\{dst}", console=False),
    "move": FilesystemEvent(r"Moving {kind}: ...\{src} -> ...\{dst}", console=False),
    "extract": FilesystemEvent(r"Extracting archive: ...\{src} -> ...\{dst}", console=False),
    "post_processing_started": LogEvent("Unpacking subtitles to {destination}", LogColor.BANNER, bold=True),
    "post_processing_completed": LogEvent(
        "Unpacked {extracted}, moved {moved} subtitles to {destination}", LogColor.SUCCESS
    ),
    "post_processing_no_files": LogEvent(
        "No subtitles unpacked or moved (extracted {extracted}, moved {moved})", LogColor.FAIL
    ),
    "post_processing_failed": LogEvent("Could not unpack subtitles: {reason}", LogColor.FAIL),
    # config.*
    "config.changed": LogEvent("Config change: {change}", console=False),
    "config.committed": LogEvent("Config session committed to {filename}", console=False),
    "config.reverted": LogEvent("Reverting uncommitted config changes", console=False),
    "config.schema_mismatch": LogEvent("Config schema mismatch, repairing", console=False),
    "config.key_removed": LogEvent("Removing obsolete config key {key}", console=False),
    "config.key_added": LogEvent("Adding missing config key {key}", console=False),
    "config.reset": LogEvent("Resetting config to defaults at {path}", console=False),
    "config.restored": LogEvent("Restoring last known good config from {path}", console=False),
    "config.restore_attempt": LogEvent("Config missing or unreadable, attempting restore from backup", console=False),
    "config.unreadable_after_restore": LogEvent(
        "Config is unreadable after restore, resetting to defaults", console=False
    ),
    "config.integrity_passed": LogEvent("Config integrity check passed", console=False),
    "config.repair_succeeded": LogEvent("Config repair succeeded", console=False),
    "config.repair_failed": LogEvent("Config repair failed, resetting to defaults", console=False),
    "config.write_failed": LogEvent("Failed to write config to {filename}: {reason}", console=False),
    "config.read": LogEvent("Read json file from {filename}", console=False),
    "config.wrote": LogEvent("Wrote config to {filename}", console=False),
    # http.*
    "http.request_failed": LogEvent("Request failed for {url}: {reason}", console=False),
    "http.bad_status": LogEvent("Request to {url} returned status {status_code}", console=False),
    # registry.*
    "registry.key_deleting": LogEvent("Deleting registry key: {key}", console=False),
    "registry.context_menu_removing": LogEvent("Removing Subsearch context menu from registry", console=False),
    "registry.key_missing": LogEvent("Registry key missing, could not write {sub_key}\\{value_name}", console=False),
    "registry.reconcile_skipped": LogEvent(
        "Skipping registry reconcile: MSI installer owns the context menu keys", console=False
    ),
    "registry.matches_absent": LogEvent("Registry matches config: context menu absent", console=False),
    "registry.matches_current": LogEvent("Registry matches config: context menu up to date", console=False),
    "registry.value_updated": LogEvent("Registry updated: {name}", console=False),
    "registry.long_paths_disabled": LogEvent(
        "Win32 long paths are not enabled, long file names may fail", console=False
    ),
    "registry.long_paths_key_missing": LogEvent(
        "Win32 long paths registry key not found, assuming disabled", console=False
    ),
    "registry.long_paths_check_failed": LogEvent("Failed to check long path status: {reason}", console=False),
    # imdb.*
    "imdb.connecting": LogEvent("Connecting to IMDb to look up titles matching {term!r}"),
    "imdb.suggestions_failed": LogEvent("IMDb connection failed while fetching suggestions for {term!r}"),
    "imdb.no_suggestions": LogEvent("IMDb returned no suggestions for {term!r}"),
    "imdb.suggestions": LogEvent("IMDb returned {count} title suggestion(s) for {term!r}"),
    "imdb.lookup_failed": LogEvent("IMDb connection failed while looking up {title!r}"),
    "imdb.no_results": LogEvent("IMDb returned no results for {title!r}", console=False),
    "imdb.matched": LogEvent("IMDb matched {title!r} -> {imdb_id}", console=False),
    "imdb.no_match": LogEvent(
        "IMDb lookup found no matching entry for {title!r} ({year}, tvseries={tvseries})", console=False
    ),
    # provider.*
    "provider.mirror_tried": LogEvent("{provider}: trying mirror {url}", console=False),
    "provider.no_mirror_responded": LogEvent("{provider}: no mirror responded", LogColor.WARN),
    "provider.structure_invalid": LogEvent(
        "{provider}: mirror responded but page structure was invalid", LogColor.WARN
    ),
    "provider.unrecognized_response": LogEvent("{provider} response was unrecognized: {reason}", console=False),
    "provider.skipped_no_api_key": LogEvent(
        "{provider} skipped: no API key configured. Add your Subsource API key in settings.", LogColor.WARN
    ),
    "provider.opensubtitles_down": LogEvent("opensubtitles is down: {reason}", LogColor.FAIL),
    "provider.subsource_status": LogEvent("{url} status_code: {status_code} {reason}", console=False),
    "provider.filename_sanitized": LogEvent("Filename sanitized: {original!r} -> {sanitized!r}", console=False),
    # diagnostics.*
    "diagnostics.healthy": LogEvent("{provider}: healthy, resetting failed_attempts to 0", console=False),
    "diagnostics.unhealthy": LogEvent(
        "{provider}: unhealthy ({status}, found {found}), failed_attempts {previous} -> {updated}", console=False
    ),
    "diagnostics.due": LogEvent("Providers due for diagnostic (threshold={threshold}): {providers}"),
    "diagnostics.running": LogEvent("Running diagnostics for: {providers}"),
    "diagnostics.probing": LogEvent("Probing {provider}", console=False),
    "diagnostics.skipped_no_api_key": LogEvent("{provider}: skipped, missing API key", LogColor.WARN),
    "diagnostics.result": LogEvent("{provider}: {status} ({diagnostic_status}, found {found})"),
    # fs.*
    "fs.creating": LogEvent("Creating {path}", console=False),
    "fs.hashing": LogEvent("Calculating hash of video file", console=False),
    "fs.invalid_file_size": LogEvent("Invalid file size, {size} bytes", console=False),
    "fs.destination_missing": LogEvent(
        "Destination directory {path} does not exist, moving to {fallback} instead", console=False
    ),
    "fs.archive_oversize": LogEvent("Archive uncompressed size {size} exceeds limit, skipping", console=False),
    "fs.archive_unsafe_path": LogEvent("Skipping unsafe path in archive: {filename}", console=False),
    "fs.archive_unreadable": LogEvent("Skipping unreadable archive {name}\n{traceback}", console=False),
    # download.*
    "download.subtitle": LogEvent("{provider:<14}{position}/{size} {subtitle_name}"),
    "download.not_zip": LogEvent("{provider}: {subtitle_name} is not a zip, skipping download", console=False),
    "download.started": LogEvent("Download started for {filename}"),
    "download.progress": LogEvent("Downloading {percentage}%"),
    "download.completed": LogEvent("Download complete"),
    # update.*
    "update.failed": LogEvent("Failed to download MSI file. HTTP Status Code: {status_code}", LogColor.FAIL),
    "update.downloaded": LogEvent("MSI file downloaded to: {destination}"),
    # pipeline.*
    "pipeline.diagnostics_flagged": LogEvent("Provider diagnostics flagged: {message}", LogColor.WARN),
    "pipeline.provider_changed": LogEvent("{provider} may have changed, unrecognized response", LogColor.WARN),
    "pipeline.summary_succeeded": LogEvent("{summary}", LogColor.MATCH),
    "pipeline.summary_failed": LogEvent("{summary}", LogColor.FAIL),
    "pipeline.finished": LogEvent("Finished in {seconds} seconds", LogColor.FINISH),
    # boot.*
    "boot.argv": LogEvent("sys.argv: {argv}", console=False),
    "boot.video_file": LogEvent("Video file {presence}: {path}", console=False),
    "boot.verifying": LogEvent("Verifying files and paths"),
    "boot.tray_init": LogEvent("Initializing system tray icon", console=False),
    "boot.gui_warmup": LogEvent("GUI warmup triggered", console=False),
    "boot.long_paths_disabled": LogEvent(
        "Win32 long paths disabled; paths >260 chars may fail. Set LongPathsEnabled=1 and reboot."
    ),
    "boot.long_paths_help": LogEvent("https://github.com/vagabondHustler/Win32LongPaths"),
    # thread.*
    "thread.submitting": LogEvent("Submitting {count} thread(s): {names}", console=False),
    "thread.failed": LogEvent("Thread {name} raised an exception\n{traceback}", console=False),
    "thread.completed": LogEvent("Thread {name} completed", console=False),
    "thread.joined": LogEvent("All threads joined: {names}", console=False),
    # flow.*
    "flow.exiting_gui": LogEvent("Exiting GUI", console=False),
    "flow.filename_has_spaces": LogEvent("{filename} contains spaces, result may vary"),
    # tray.*
    "tray.added": LogEvent("Subsearch was added to the system tray", console=False),
    "tray.removed": LogEvent("Subsearch was removed from the system tray", console=False),
    # guard.*
    "guard.step_skipped": LogEvent("skipped {qualified_name}", console=False),
    "guard.step_called": LogEvent("called {qualified_name}", console=False),
    "guard.single_instance": LogEvent("Single-instance enforcement: {single_instance}", console=False),
    "guard.single_instance_disabled": LogEvent("Single-instance disabled, skipping mutex", console=False),
    "guard.mutex_acquired": LogEvent("Mutex acquired: {guid}", console=False),
    "guard.mutex_released": LogEvent("Mutex released: {guid}", console=False),
    # run_conditions.*
    "run_conditions.evaluated": LogEvent("run_conditions [{step}]: {detail} -> {decision}", console=False),
    # tracker.*
    "tracker.manifest_unreadable": LogEvent("Unreadable file manifest at {path}, starting fresh", console=False),
    "tracker.refusing_untracked": LogEvent("Refusing to delete untracked path {path}", console=False),
    "tracker.reclaiming": LogEvent("Reclaiming leftover temp path {path}", console=False),
    # score.*
    "score.exact_token_match": LogEvent("Fuzzy match: exact token match for {from_provider!r}", console=False),
    "score.breakdown": LogEvent(
        "Fuzzy match: {score}% for {from_provider!r} (base {base}, mismatch ×{mismatch})", console=False
    ),
}


def format_change(key: str, old: Any, new: Any) -> str:
    return f"{key}: {old!r} → {new!r}"


def session_header() -> str:
    started_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"\x1c\n{started_at}\n"


def render(event_key: str, **values: Any) -> tuple[str, LogEvent]:
    event = LOG_EVENTS[event_key]
    return event.render(**values), event


def dataclass_lines(instance: DataclassInstance) -> list[str]:
    if not dataclasses.is_dataclass(instance):
        raise ValueError("Input is not a dataclass instance.")
    lines = [LOG_EVENTS["banner"].render(title=instance.__class__.__name__)]
    for dataclass_field in dataclasses.fields(instance):
        value = getattr(instance, dataclass_field.name)
        lines.extend(_field_lines(dataclass_field.name, value))
    return lines


def _field_lines(field_name: str, value: Any) -> list[str]:
    if isinstance(value, dict):
        return [line for key, nested in value.items() for line in _field_lines(f"{field_name}.{key}", nested)]
    return [f"{field_name} = {_format_value(value)}"]


def _format_value(value: Any) -> str:
    if isinstance(value, bool):
        return str(value).lower()
    return str(value)
