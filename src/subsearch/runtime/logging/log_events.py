from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from subsearch.runtime.logging import log_sanitizer
from subsearch.runtime.models.model import DataclassInstance

BANNER_COLOR = "#fab387"
MATCH_COLOR = "#a6e3a1"
DONE_COLOR = "#89b4fa"


@dataclass(frozen=True, slots=True)
class LogEvent:
    template: str
    color: Optional[str] = None
    bold: bool = False


LOG_EVENTS: dict[str, LogEvent] = {
    "banner": LogEvent("--- [{title}] ---", BANNER_COLOR, bold=True),
    "task_completed": LogEvent("Tasks completed", DONE_COLOR),
    "subtitle_match": LogEvent("{provider:<14}{percentage:>3}% {subtitle_name}", MATCH_COLOR),
    "subtitle_rejected": LogEvent("{provider:<14}{percentage:>3}% {subtitle_name}"),
    "provider_skips": LogEvent("{provider:<14}skipped {total} ({breakdown})"),
    "remove": LogEvent(r"Removing {kind}: ...\{src}"),
    "rename": LogEvent(r"Renaming {kind}: ...\{src} -> ...\{dst}"),
    "move": LogEvent(r"Moving {kind}: ...\{src} -> ...\{dst}"),
    "extract": LogEvent(r"Extracting archive: ...\{src} -> ...\{dst}"),
}


FILESYSTEM_EVENTS = {"remove", "rename", "move", "extract"}


def session_header() -> str:
    started_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"\x1c\n{started_at}\n"


def render(event_key: str, **values: Any) -> tuple[str, Optional[str], bool]:
    event = LOG_EVENTS[event_key]
    if event_key in FILESYSTEM_EVENTS:
        values = _filesystem_values(values)
    text = event.template.format(**values)
    return text, event.color, event.bold


def _filesystem_values(values: dict[str, Any]) -> dict[str, Any]:
    source: Path = values["src"]
    destination: Optional[Path] = values.get("dst")
    return {"kind": _path_kind(source), "src": _shorten(source), "dst": _shorten(destination)}


def _path_kind(path: Path) -> str:
    if path.is_file():
        return "file"
    if path.is_dir():
        return "directory"
    return "item"


def _shorten(path: Optional[Path]) -> Optional[Path]:
    return path.relative_to(path.parent.parent) if path else None


def dataclass_lines(instance: DataclassInstance) -> list[str]:
    return log_sanitizer.dataclass_lines(instance, LOG_EVENTS["banner"].template)
