from pathlib import Path

import pytest

from subsearch.runtime.logging import events, rendering
from subsearch.runtime.logging.events import LogEvent

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
    "season": 1,
    "episode": 7,
    "seasons": 5,
    "episodes": 13,
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
    "member_count": 3,
    "listing": "  sub.srt (1234 bytes)",
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


def test_extract_renders_archive_name() -> None:
    archive = Path("36e8699881f347168fb7ee414bee7c11_yifysubtitles_mortal.kombat.2021.webrip.x264-ion10_2.zip")
    assert rendering.render(LogEvent.EXTRACT, src=archive, dst=Path("out")) == f"Extracting {archive.name}"
