from pathlib import Path

import pytest

from subsearch.runtime.keys import LogEvent
from subsearch.runtime.logging import events, rendering

_REPRESENTATIVE_VALUES = {
    "title": "Example",
    "filename": "movie.mkv",
    "provider": "opensubtitles",
    "percentage": 95,
    "subtitle_name": "movie.2021.srt",
    "total": 3,
    "breakdown": "language=2, hi=1",
    "src": Path("a/b/c.zip"),
    "dst": Path("a/b/out"),
    "destination": "C:/tmp",
    "extracted": 2,
    "moved": 2,
    "reason": "boom",
    "change": "search.accept_threshold: 90 → 50",
    "url": "https://example.test",
    "status_code": 503,
    "cloudflare": "challenge",
    "key": "search.accept_threshold",
    "path": Path("C:/tmp/x"),
    "filename_field": "movie.mkv",
    "sub_key": r"Software\Classes",
    "value_name": "command",
    "name": "Subsearch",
    "term": "matrix",
    "count": 4,
    "title_field": "The Matrix",
    "imdb_id": "tt0133093",
    "year": 1999,
    "tvseries": False,
    "status": "healthy",
    "found": 5,
    "accepted": 3,
    "rejected": 2,
    "action": "set value",
    "target": r"Software\Classes\command",
    "previous": 0,
    "updated": 1,
    "threshold": 3,
    "providers": "opensubtitles, subsource",
    "diagnostic_status": "ok",
    "size": 1234,
    "fallback": Path("C:/fallback"),
    "position": 1,
    "summary": "Downloaded: 1/3",
    "message": "opensubtitles",
    "score": 95,
    "seconds": 1.23,
    "argv": ["subsearch"],
    "presence": "found",
    "names": "a, b",
    "traceback": "Traceback ...",
    "single_instance": True,
    "guid": "{GUID}",
    "step": "download",
    "detail": "x=True",
    "decision": "run",
    "from_provider": "movie.2021",
    "base": 80,
    "mismatch": "0.90",
    "qualified_name": "Foo.bar",
    "destination_field": "C:/out.msi",
    "original": "raw'name",
    "sanitized": "raw_name",
}


@pytest.mark.parametrize("event_key", sorted(LogEvent, key=str))
def test_every_event_renders_without_keyerror(event_key: LogEvent) -> None:
    if event_key in events.FILESYSTEM_EVENTS:
        rendering.render(event_key, src=Path("a/b/c.zip"), dst=Path("a/b/out"))
        return
    try:
        rendering.render(event_key, **_REPRESENTATIVE_VALUES)
    except KeyError as missing:
        pytest.fail(f"{event_key} template references {missing} not in representative values")


def test_log_event_enum_matches_events_table() -> None:
    assert set(LogEvent) == set(events.EVENTS)


# The console is a plain-language progress feed: phase markers, the found subtitle
# list, downloads, and a handful of saved/restored/failed lines the user can act on.
# Everything else is forensic detail that belongs only in the log file. This set is the
# contract; promoting a new event to the console is a deliberate edit to this list.
CONSOLE_FACING_EVENTS = {
    LogEvent.BANNER,
    LogEvent.VIDEO_FILE_SELECTED,
    LogEvent.SUBTITLE_MATCH,
    LogEvent.SUBTITLE_REJECTED,
    LogEvent.RENAME,
    LogEvent.EXTRACT,
    LogEvent.CONFIG_COMMITTED,
    LogEvent.CONFIG_REVERTED,
    LogEvent.CONFIG_RESET,
    LogEvent.CONFIG_RESTORED,
    LogEvent.IMDB_CONNECTING,
    LogEvent.DOWNLOAD_SUBTITLE,
    LogEvent.UPDATE_FAILED,
    LogEvent.BOOT_LONG_PATHS_DISABLED,
    LogEvent.BOOT_LONG_PATHS_HELP,
}


def test_console_facing_events_match_contract() -> None:
    assert events.CONSOLE_EVENTS == CONSOLE_FACING_EVENTS
