from pathlib import Path

import pytest

from subsearch.runtime.logging import log_events

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


@pytest.mark.parametrize("event_key", sorted(log_events.LOG_EVENTS))
def test_every_event_renders_without_keyerror(event_key: str) -> None:
    event = log_events.LOG_EVENTS[event_key]
    if isinstance(event, log_events.FilesystemEvent):
        event.render(src=Path("a/b/c.zip"), dst=Path("a/b/out"))
        return
    try:
        event.render(**_REPRESENTATIVE_VALUES)
    except KeyError as missing:
        pytest.fail(f"{event_key} template references {missing} not in representative values")
