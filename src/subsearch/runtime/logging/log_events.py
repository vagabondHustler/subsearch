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
    "config.changed": LogEvent("Config change: {change}", console=False),
    "http.request_failed": LogEvent("Request failed for {url}: {reason}", console=False),
    "http.bad_status": LogEvent("Request to {url} returned status {status_code}", console=False),
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
