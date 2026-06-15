import dataclasses
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from subsearch.runtime.keys import LogEvent
from subsearch.runtime.logging import events
from subsearch.runtime.models import DataclassInstance


class LogColor:
    BANNER = "#fab387"  # orange — section banners / selections
    MATCH = "#a6e3a1"  # green — accepted subtitle / success
    SUCCESS = "#89b4fa"  # blue — task completed / done
    WARN = "#f9e2af"  # yellow — soft warnings
    FAIL = "#f38ba8"  # red — failures
    FINISH = "#f2cdcd"  # peach — run summary line


def render(event_key: LogEvent, **values: Any) -> str:
    template = events.EVENTS[event_key]
    if event_key in events.FILESYSTEM_EVENTS:
        return template.format(**_filesystem_values(values))
    return template.format(**values)


def _filesystem_values(values: dict[str, Any]) -> dict[str, Any]:
    source: Path = values["src"]
    destination: Optional[Path] = values.get("dst")
    return {
        "kind": _path_kind(source),
        "src": _shorten(source),
        "dst": _shorten(destination),
        "src_name": source.name,
        "dst_name": destination.name if destination is not None else None,
    }


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


def format_change(key: str, old: Any, new: Any) -> str:
    return f"{key}: {old!r} → {new!r}"


def session_header() -> str:
    started_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"\x1c\n{started_at}\n"


def dataclass_lines(instance: DataclassInstance) -> list[str]:
    if not dataclasses.is_dataclass(instance):
        raise ValueError("Input is not a dataclass instance.")
    lines = [f"--- [{instance.__class__.__name__}] ---"]
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
