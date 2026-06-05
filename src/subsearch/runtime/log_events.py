import dataclasses
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from subsearch.runtime.model import DataclassInstance

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
    color = _match_color(values) if event_key == "subtitle_match" else event.color
    return text, color, event.bold


def _match_color(values: dict[str, Any]) -> Optional[str]:
    return MATCH_COLOR if values["percentage"] >= values["threshold"] else None


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


SECRET_FIELDS = {"subsource_api_key"}


def _secret_status(value: object) -> str:
    api_key = str(value)
    if not api_key:
        return "<not set>"
    return "<valid key>" if re.match(r"^sk_[0-9a-f]+$", api_key) else "<invalid key>"


def dataclass_lines(instance: DataclassInstance) -> list[str]:
    if not dataclasses.is_dataclass(instance):
        raise ValueError("Input is not a dataclass instance.")
    lines = [LOG_EVENTS["banner"].template.format(title=instance.__class__.__name__)]
    for field in dataclasses.fields(instance):
        value = getattr(instance, field.name)
        if field.name in SECRET_FIELDS:
            value = _secret_status(value)
        padding = " " * (30 - len(field.name))
        lines.append(f"{field.name}:{padding}{value}")
    return lines
