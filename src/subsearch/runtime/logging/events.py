from enum import StrEnum


class LogEvent(StrEnum):
    BANNER = "banner"
    EXITING = "exiting"
    VIDEO_FILE_SELECTED = "video_file_selected"
    SEARCH_TERM_SET = "search_term_set"
    SUBTITLE_MATCH = "subtitle_match"
    SUBTITLE_REJECTED = "subtitle_rejected"
    PROVIDER_SKIPS = "provider_skips"
    REMOVE = "remove"
    RENAME = "rename"
    MOVE = "move"
    EXTRACT = "extract"
    POST_PROCESSING_STARTED = "post_processing_started"
    POST_PROCESSING_COMPLETED = "post_processing_completed"
    POST_PROCESSING_NO_FILES = "post_processing_no_files"
    POST_PROCESSING_FAILED = "post_processing_failed"
    SEARCH_COMPLETED = "search_completed"
    EXTRACT_COMPLETED = "extract_completed"
    RENAME_COMPLETED = "rename_completed"
    MOVE_BEST_COMPLETED = "move_best_completed"
    MOVE_ALL_COMPLETED = "move_all_completed"
    CLEANUP_COMPLETED = "cleanup_completed"

    CONFIG_CHANGED = "config.changed"
    CONFIG_COMMITTED = "config.committed"
    CONFIG_REVERTED = "config.reverted"
    CONFIG_SCHEMA_MISMATCH = "config.schema_mismatch"
    CONFIG_KEY_REMOVED = "config.key_removed"
    CONFIG_KEY_ADDED = "config.key_added"
    CONFIG_RESET = "config.reset"
    CONFIG_RESTORED = "config.restored"
    CONFIG_RESTORE_ATTEMPT = "config.restore_attempt"
    CONFIG_UNREADABLE_AFTER_RESTORE = "config.unreadable_after_restore"
    CONFIG_INTEGRITY_PASSED = "config.integrity_passed"
    CONFIG_REPAIR_SUCCEEDED = "config.repair_succeeded"
    CONFIG_REPAIR_FAILED = "config.repair_failed"
    CONFIG_WRITE_FAILED = "config.write_failed"
    CONFIG_READ = "config.read"
    CONFIG_WROTE = "config.wrote"

    HTTP_REQUEST_FAILED = "http.request_failed"
    HTTP_BAD_STATUS = "http.bad_status"

    REGISTRY_ATTEMPTING = "registry.attempting"
    REGISTRY_KEY_DELETING = "registry.key_deleting"
    REGISTRY_CONTEXT_MENU_REMOVING = "registry.context_menu_removing"
    REGISTRY_KEY_MISSING = "registry.key_missing"
    REGISTRY_MATCHES_ABSENT = "registry.matches_absent"
    REGISTRY_MATCHES_CURRENT = "registry.matches_current"
    REGISTRY_VALUE_UPDATED = "registry.value_updated"
    REGISTRY_LONG_PATHS_DISABLED = "registry.long_paths_disabled"
    REGISTRY_LONG_PATHS_KEY_MISSING = "registry.long_paths_key_missing"
    REGISTRY_LONG_PATHS_CHECK_FAILED = "registry.long_paths_check_failed"

    IMDB_CONNECTING = "imdb.connecting"
    IMDB_SUGGESTIONS_FAILED = "imdb.suggestions_failed"
    IMDB_NO_SUGGESTIONS = "imdb.no_suggestions"
    IMDB_SUGGESTIONS = "imdb.suggestions"
    IMDB_EPISODES_FAILED = "imdb.episodes_failed"
    IMDB_EPISODES = "imdb.episodes"
    GESTDOWN_SEASONS_FAILED = "gestdown.seasons_failed"
    GESTDOWN_SEASONS = "gestdown.seasons"
    GESTDOWN_EPISODES_FAILED = "gestdown.episodes_failed"
    GESTDOWN_EPISODES = "gestdown.episodes"
    IMDB_LOOKUP_FAILED = "imdb.lookup_failed"
    IMDB_NO_RESULTS = "imdb.no_results"
    IMDB_MATCHED = "imdb.matched"
    IMDB_NO_MATCH = "imdb.no_match"

    PROVIDER_SEARCHING = "provider.searching"
    PROVIDER_SEARCH_RESULT = "provider.search_result"
    PROVIDER_MIRROR_TRIED = "provider.mirror_tried"
    PROVIDER_NO_MIRROR_RESPONDED = "provider.no_mirror_responded"
    PROVIDER_STRUCTURE_INVALID = "provider.structure_invalid"
    PROVIDER_UNRECOGNIZED_RESPONSE = "provider.unrecognized_response"
    PROVIDER_SKIPPED_NO_API_KEY = "provider.skipped_no_api_key"
    PROVIDER_SKIP_REASON = "provider.skip_reason"
    PROVIDER_OPENSUBTITLES_DOWN = "provider.opensubtitles_down"
    PROVIDER_SUBSOURCE_STATUS = "provider.subsource_status"
    PROVIDER_GESTDOWN_STATUS = "provider.gestdown_status"
    PROVIDER_FILENAME_SANITIZED = "provider.filename_sanitized"

    DIAGNOSTICS_HEALTHY = "diagnostics.healthy"
    DIAGNOSTICS_UNHEALTHY = "diagnostics.unhealthy"
    DIAGNOSTICS_DUE = "diagnostics.due"
    DIAGNOSTICS_RUNNING = "diagnostics.running"
    DIAGNOSTICS_PROBING = "diagnostics.probing"
    DIAGNOSTICS_SKIPPED_NO_API_KEY = "diagnostics.skipped_no_api_key"
    DIAGNOSTICS_RESULT = "diagnostics.result"
    DIAGNOSTICS_COMPLETED = "diagnostics.completed"
    DIAGNOSTICS_DUE_COMPLETED = "diagnostics.due_completed"

    FS_CREATING = "fs.creating"
    FS_HASHING = "fs.hashing"
    FS_INVALID_FILE_SIZE = "fs.invalid_file_size"
    FS_DESTINATION_MISSING = "fs.destination_missing"
    FS_ARCHIVE_OVERSIZE = "fs.archive_oversize"
    FS_ARCHIVE_UNSAFE_PATH = "fs.archive_unsafe_path"
    FS_ARCHIVE_UNREADABLE = "fs.archive_unreadable"

    DOWNLOAD_SUBTITLE = "download.subtitle"
    DOWNLOAD_NOT_ZIP = "download.not_zip"
    DOWNLOAD_STARTED = "download.started"
    DOWNLOAD_PROGRESS = "download.progress"
    DOWNLOAD_COMPLETED = "download.completed"
    DOWNLOADS_COMPLETED = "download.all_completed"
    DOWNLOAD_FAILED = "download.failed"

    UPDATE_FAILED = "update.failed"
    UPDATE_DOWNLOADED = "update.downloaded"
    UPDATE_CHANGELOG_FAILED = "update.changelog_failed"

    PIPELINE_DIAGNOSTICS_FLAGGED = "pipeline.diagnostics_flagged"
    PIPELINE_PROVIDER_CHANGED = "pipeline.provider_changed"
    PIPELINE_SUMMARY_SUCCEEDED = "pipeline.summary_succeeded"
    PIPELINE_SUMMARY_FAILED = "pipeline.summary_failed"
    PIPELINE_FINISHED = "pipeline.finished"

    BOOT_ARGV = "boot.argv"
    BOOT_VIDEO_FILE = "boot.video_file"
    BOOT_VERIFYING = "boot.verifying"
    BOOT_TRAY_INIT = "boot.tray_init"
    BOOT_UI_LAZY = "boot.ui_lazy"
    BOOT_UI_LAZY_DONE = "boot.ui_lazy_done"
    BOOT_UI_OPENED = "boot.ui_opened"
    BOOT_UI_CLOSED = "boot.ui_closed"
    BOOT_COMPLETED = "boot.completed"
    BOOT_WORKSPACE_CLOSED = "boot.workspace_closed"
    BOOT_LONG_PATHS_DISABLED = "boot.long_paths_disabled"
    BOOT_LONG_PATHS_HELP = "boot.long_paths_help"

    THREAD_SUBMITTING = "thread.submitting"
    THREAD_FAILED = "thread.failed"
    THREAD_COMPLETED = "thread.completed"
    THREAD_JOINED = "thread.joined"

    FLOW_FILENAME_HAS_SPACES = "flow.filename_has_spaces"

    TRAY_ADDED = "tray.added"
    TRAY_REMOVED = "tray.removed"

    TASK_FAILED = "task.failed"

    GUARD_STEP_SKIPPED = "guard.step_skipped"
    GUARD_STEP_CALLED = "guard.step_called"
    GUARD_SINGLE_INSTANCE = "guard.single_instance"
    GUARD_SINGLE_INSTANCE_DISABLED = "guard.single_instance_disabled"
    GUARD_MUTEX_ACQUIRED = "guard.mutex_acquired"
    GUARD_MUTEX_RELEASED = "guard.mutex_released"

    RUN_CONDITIONS_EVALUATED = "run_conditions.evaluated"

    TRACKER_TRACKING = "tracker.tracking"
    TRACKER_RELEASED = "tracker.released"
    TRACKER_DISCARDING_STALE = "tracker.discarding_stale"
    TRACKER_MANIFEST_UNREADABLE = "tracker.manifest_unreadable"
    TRACKER_REFUSING_UNTRACKED = "tracker.refusing_untracked"
    TRACKER_RECLAIMING = "tracker.reclaiming"

    SCORE_EXACT_TOKEN_MATCH = "score.exact_token_match"
    SCORE_BREAKDOWN = "score.breakdown"


EVENTS: dict[LogEvent, str] = {
    LogEvent.BANNER: "--- [{title}] ---",
    LogEvent.EXITING: "Exiting",
    LogEvent.VIDEO_FILE_SELECTED: "Selected {filename}",
    LogEvent.SEARCH_TERM_SET: "Search term set: {term}",
    LogEvent.SUBTITLE_MATCH: "{subtitle_name}",
    LogEvent.SUBTITLE_REJECTED: "{subtitle_name}",
    LogEvent.PROVIDER_SKIPS: "{provider:<14}skipped {total} ({breakdown})",
    LogEvent.REMOVE: "Removing {kind}: {src}",
    LogEvent.RENAME: "Renamed to {dst_name}",
    LogEvent.MOVE: "Moving {kind}: {src} -> {dst}",
    LogEvent.EXTRACT: "Extracting {src_name}",
    LogEvent.POST_PROCESSING_STARTED: "Unpacking subtitles to {destination}",
    LogEvent.POST_PROCESSING_COMPLETED: "Moved {moved} subtitles to {destination}",
    LogEvent.POST_PROCESSING_NO_FILES: "No subtitles unpacked or moved (moved {moved})",
    LogEvent.POST_PROCESSING_FAILED: "Could not unpack subtitles: {reason}",
    LogEvent.SEARCH_COMPLETED: "Search completed",
    LogEvent.EXTRACT_COMPLETED: "Extraction completed",
    LogEvent.RENAME_COMPLETED: "Rename completed",
    LogEvent.MOVE_BEST_COMPLETED: "Best subtitle moved",
    LogEvent.MOVE_ALL_COMPLETED: "All subtitles moved",
    LogEvent.CLEANUP_COMPLETED: "Cleanup completed",
    LogEvent.CONFIG_CHANGED: "Config change: {change}",
    LogEvent.CONFIG_COMMITTED: "Settings saved",
    LogEvent.CONFIG_REVERTED: "Discarded unsaved settings",
    LogEvent.CONFIG_SCHEMA_MISMATCH: "Config schema mismatch, repairing",
    LogEvent.CONFIG_KEY_REMOVED: "Removing obsolete config key {key}",
    LogEvent.CONFIG_KEY_ADDED: "Adding missing config key {key}",
    LogEvent.CONFIG_RESET: "Settings reset to defaults",
    LogEvent.CONFIG_RESTORED: "Restored settings from backup",
    LogEvent.CONFIG_RESTORE_ATTEMPT: "Config missing or unreadable, attempting restore from backup",
    LogEvent.CONFIG_UNREADABLE_AFTER_RESTORE: "Config is unreadable after restore, resetting to defaults",
    LogEvent.CONFIG_INTEGRITY_PASSED: "Config integrity check passed",
    LogEvent.CONFIG_REPAIR_SUCCEEDED: "Config repair succeeded",
    LogEvent.CONFIG_REPAIR_FAILED: "Config repair failed, resetting to defaults",
    LogEvent.CONFIG_WRITE_FAILED: "Failed to write config to {filename}: {reason}",
    LogEvent.CONFIG_READ: "Read json file from {filename}",
    LogEvent.CONFIG_WROTE: "Wrote config to {filename}",
    LogEvent.HTTP_REQUEST_FAILED: "Request failed for {url}: {reason}",
    LogEvent.HTTP_BAD_STATUS: "Request to {url} returned status {status_code}",
    LogEvent.REGISTRY_ATTEMPTING: "Attempting registry {action}: {target}",
    LogEvent.REGISTRY_KEY_DELETING: "Deleting registry key: {key}",
    LogEvent.REGISTRY_CONTEXT_MENU_REMOVING: "Removing Subsearch context menu from registry",
    LogEvent.REGISTRY_KEY_MISSING: "Registry key missing, could not write {sub_key}\\{value_name}",
    LogEvent.REGISTRY_MATCHES_ABSENT: "Registry matches config: context menu absent",
    LogEvent.REGISTRY_MATCHES_CURRENT: "Registry matches config: context menu up to date",
    LogEvent.REGISTRY_VALUE_UPDATED: "Registry updated: {name}",
    LogEvent.REGISTRY_LONG_PATHS_DISABLED: "Win32 long paths are not enabled, long file names may fail",
    LogEvent.REGISTRY_LONG_PATHS_KEY_MISSING: "Win32 long paths registry key not found, assuming disabled",
    LogEvent.REGISTRY_LONG_PATHS_CHECK_FAILED: "Failed to check long path status: {reason}",
    LogEvent.IMDB_CONNECTING: "Fuzzy matching {term!r}",
    LogEvent.IMDB_SUGGESTIONS_FAILED: "IMDb connection failed while fetching suggestions for {term!r}",
    LogEvent.IMDB_NO_SUGGESTIONS: "IMDb returned no suggestions for {term!r}",
    LogEvent.IMDB_SUGGESTIONS: "IMDb returned {count} title suggestion(s) for {term!r}",
    LogEvent.IMDB_EPISODES_FAILED: "IMDb connection failed while fetching episodes for {imdb_id} season {season}",
    LogEvent.IMDB_EPISODES: "IMDb returned {seasons} season(s) and {episodes} episode(s) for {imdb_id}",
    LogEvent.GESTDOWN_SEASONS_FAILED: "Gestdown returned no seasons for '{title}'",
    LogEvent.GESTDOWN_SEASONS: "Gestdown returned {seasons} season(s) for '{title}'",
    LogEvent.GESTDOWN_EPISODES_FAILED: "Gestdown returned no episodes for '{title}' season {season}",
    LogEvent.GESTDOWN_EPISODES: "Gestdown returned {episodes} episode(s) for '{title}' season {season}",
    LogEvent.IMDB_LOOKUP_FAILED: "IMDb connection failed while looking up {title!r}",
    LogEvent.IMDB_NO_RESULTS: "IMDb returned no results for {title!r}",
    LogEvent.IMDB_MATCHED: "IMDb matched {title!r} -> {imdb_id}",
    LogEvent.IMDB_NO_MATCH: "IMDb lookup found no matching entry for {title!r} ({year}, tvseries={tvseries})",
    LogEvent.PROVIDER_SEARCHING: "{provider}: searching",
    LogEvent.PROVIDER_SEARCH_RESULT: "{provider}: found {found} ({accepted} accepted, {rejected} rejected)",
    LogEvent.PROVIDER_MIRROR_TRIED: "{provider}: trying mirror {url}",
    LogEvent.PROVIDER_NO_MIRROR_RESPONDED: "{provider}: no mirror responded",
    LogEvent.PROVIDER_STRUCTURE_INVALID: "{provider}: mirror responded but page structure was invalid",
    LogEvent.PROVIDER_UNRECOGNIZED_RESPONSE: "{provider} response was unrecognized: {reason}",
    LogEvent.PROVIDER_SKIPPED_NO_API_KEY: (
        "{provider} skipped: no API key configured. Add your Subsource API key in settings."
    ),
    LogEvent.PROVIDER_SKIP_REASON: "{reason}",
    LogEvent.PROVIDER_OPENSUBTITLES_DOWN: "opensubtitles is down: {reason}",
    LogEvent.PROVIDER_SUBSOURCE_STATUS: "{url} status_code: {status_code} {reason}",
    LogEvent.PROVIDER_GESTDOWN_STATUS: "{url} status_code: {status_code} {reason}",
    LogEvent.PROVIDER_FILENAME_SANITIZED: "Filename sanitized: {original!r} -> {sanitized!r}",
    LogEvent.DIAGNOSTICS_HEALTHY: "{provider}: healthy, resetting failed_attempts to 0",
    LogEvent.DIAGNOSTICS_UNHEALTHY: (
        "{provider}: unhealthy ({status}, found {found}), failed_attempts {previous} -> {updated}"
    ),
    LogEvent.DIAGNOSTICS_DUE: "Providers due for diagnostic (threshold={threshold}): {providers}",
    LogEvent.DIAGNOSTICS_RUNNING: "Running diagnostics for: {providers}",
    LogEvent.DIAGNOSTICS_PROBING: "Probing {provider}",
    LogEvent.DIAGNOSTICS_SKIPPED_NO_API_KEY: "{provider}: skipped, missing API key",
    LogEvent.DIAGNOSTICS_RESULT: "{provider}: {status} ({diagnostic_status}, found {found})",
    LogEvent.DIAGNOSTICS_COMPLETED: "Diagnostics completed",
    LogEvent.DIAGNOSTICS_DUE_COMPLETED: "Due diagnostics completed",
    LogEvent.FS_CREATING: "Creating {path}",
    LogEvent.FS_HASHING: "Calculating hash of video file",
    LogEvent.FS_INVALID_FILE_SIZE: "Invalid file size, {size} bytes",
    LogEvent.FS_DESTINATION_MISSING: "Destination directory {path} does not exist, moving to {fallback} instead",
    LogEvent.FS_ARCHIVE_OVERSIZE: "Archive uncompressed size {size} exceeds limit, skipping",
    LogEvent.FS_ARCHIVE_UNSAFE_PATH: "Skipping unsafe path in archive: {filename}",
    LogEvent.FS_ARCHIVE_UNREADABLE: "Skipping unreadable archive {name}\n{traceback}",
    LogEvent.DOWNLOAD_SUBTITLE: "Downloading {subtitle_name}",
    LogEvent.DOWNLOAD_NOT_ZIP: (
        "{provider}: {subtitle_name} is not a zip (status {status_code}, cloudflare {cloudflare}) "
        "from {url}, skipping download"
    ),
    LogEvent.DOWNLOAD_STARTED: "Download started for {filename}",
    LogEvent.DOWNLOAD_PROGRESS: "Downloading {percentage}%",
    LogEvent.DOWNLOAD_COMPLETED: "Download complete",
    LogEvent.DOWNLOADS_COMPLETED: "Downloads completed",
    LogEvent.DOWNLOAD_FAILED: "Download failed: {reason}",
    LogEvent.UPDATE_FAILED: "Update download failed",
    LogEvent.UPDATE_DOWNLOADED: "MSI file downloaded to: {destination}",
    LogEvent.UPDATE_CHANGELOG_FAILED: "Failed to fetch changelog: {reason}",
    LogEvent.PIPELINE_DIAGNOSTICS_FLAGGED: "Provider diagnostics flagged: {message}",
    LogEvent.PIPELINE_PROVIDER_CHANGED: "{provider} may have changed, unrecognized response",
    LogEvent.PIPELINE_SUMMARY_SUCCEEDED: "{summary}",
    LogEvent.PIPELINE_SUMMARY_FAILED: "{summary}",
    LogEvent.PIPELINE_FINISHED: "Finished in {seconds} seconds",
    LogEvent.BOOT_ARGV: "sys.argv: {argv}",
    LogEvent.BOOT_VIDEO_FILE: "Video file {presence}: {path}",
    LogEvent.BOOT_VERIFYING: "Verifying files and paths",
    LogEvent.BOOT_TRAY_INIT: "Initializing system tray icon",
    LogEvent.BOOT_UI_LAZY: "Lazy loading UI",
    LogEvent.BOOT_UI_LAZY_DONE: "Lazy loading UI done",
    LogEvent.BOOT_UI_OPENED: "UI opened",
    LogEvent.BOOT_UI_CLOSED: "UI closed",
    LogEvent.BOOT_COMPLETED: "Boot completed",
    LogEvent.BOOT_WORKSPACE_CLOSED: "Results window closed",
    LogEvent.BOOT_LONG_PATHS_DISABLED: (
        "Win32 long paths disabled; paths >260 chars may fail. Set LongPathsEnabled=1 and reboot."
    ),
    LogEvent.BOOT_LONG_PATHS_HELP: "https://github.com/vagabondHustler/Win32LongPaths",
    LogEvent.THREAD_SUBMITTING: "Submitting {count} thread(s): {names}",
    LogEvent.THREAD_FAILED: "Thread {name} raised an exception\n{traceback}",
    LogEvent.THREAD_COMPLETED: "Thread {name} completed",
    LogEvent.THREAD_JOINED: "All threads joined: {names}",
    LogEvent.FLOW_FILENAME_HAS_SPACES: "{filename} contains spaces, result may vary",
    LogEvent.TRAY_ADDED: "Subsearch was added to the system tray",
    LogEvent.TRAY_REMOVED: "Subsearch was removed from the system tray",
    LogEvent.TASK_FAILED: "{reason}",
    LogEvent.GUARD_STEP_SKIPPED: "skipped {qualified_name}",
    LogEvent.GUARD_STEP_CALLED: "called {qualified_name}",
    LogEvent.GUARD_SINGLE_INSTANCE: "Single-instance enforcement: {single_instance}",
    LogEvent.GUARD_SINGLE_INSTANCE_DISABLED: "Single-instance disabled, skipping mutex",
    LogEvent.GUARD_MUTEX_ACQUIRED: "Mutex acquired: {guid}",
    LogEvent.GUARD_MUTEX_RELEASED: "Mutex released: {guid}",
    LogEvent.RUN_CONDITIONS_EVALUATED: "run_conditions [{step}]: {detail} -> {decision}",
    LogEvent.TRACKER_TRACKING: "Tracking {path}",
    LogEvent.TRACKER_RELEASED: "Released {path}",
    LogEvent.TRACKER_DISCARDING_STALE: "Discarding stale tracked path {path}",
    LogEvent.TRACKER_MANIFEST_UNREADABLE: "Unreadable file manifest at {path}, starting fresh",
    LogEvent.TRACKER_REFUSING_UNTRACKED: "Refusing to delete untracked path {path}",
    LogEvent.TRACKER_RECLAIMING: "Reclaiming leftover temp path {path}",
    LogEvent.SCORE_EXACT_TOKEN_MATCH: "Fuzzy match: exact token match for {from_provider!r}",
    LogEvent.SCORE_BREAKDOWN: "Fuzzy match: {score}% for {from_provider!r} (base {base}, mismatch ×{mismatch})",
}

FILESYSTEM_EVENTS: frozenset[LogEvent] = frozenset({LogEvent.REMOVE, LogEvent.RENAME, LogEvent.MOVE, LogEvent.EXTRACT})

PATH_EVENTS: frozenset[LogEvent] = frozenset(
    {
        LogEvent.TRACKER_TRACKING,
        LogEvent.TRACKER_RELEASED,
        LogEvent.TRACKER_DISCARDING_STALE,
        LogEvent.TRACKER_MANIFEST_UNREADABLE,
        LogEvent.TRACKER_REFUSING_UNTRACKED,
        LogEvent.TRACKER_RECLAIMING,
        LogEvent.FS_CREATING,
        LogEvent.FS_DESTINATION_MISSING,
        LogEvent.POST_PROCESSING_STARTED,
        LogEvent.POST_PROCESSING_COMPLETED,
        LogEvent.UPDATE_DOWNLOADED,
    }
)
