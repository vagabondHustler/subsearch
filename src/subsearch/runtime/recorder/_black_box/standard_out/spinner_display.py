from collections import Counter, deque
from dataclasses import dataclass, field

from rich.console import Console, Group, RenderableType
from rich.live import Live
from rich.spinner import Spinner
from rich.text import Text

from subsearch.runtime.recorder._black_box.standard_out.severity_summary import (
    severity_summary,
)
from subsearch.runtime.recorder.config import ConsoleGroup, ConsoleLine, ConsoleSnapshot
from subsearch.runtime.recorder.console_theme import ConsoleTheme

_RESERVED_LEVELS = frozenset({"warning", "error", "critical"})
_SEVERITY_ORDER = ("clean", "warning", "error", "critical")


@dataclass(slots=True)
class _TransientLine:
    message: str
    color: str


@dataclass(slots=True)
class _SpinnerGroup:
    title: str
    spinner: Spinner
    transient_lines: deque[_TransientLine]
    theme: ConsoleTheme
    worst_severity: str = "clean"
    severity_counts: Counter[str] = field(default_factory=Counter)

    def record_severity(self, level: str) -> None:
        if level in _RESERVED_LEVELS:
            self.severity_counts[level] += 1
        if level in _SEVERITY_ORDER and _SEVERITY_ORDER.index(level) > _SEVERITY_ORDER.index(self.worst_severity):
            self.worst_severity = level

    def active_renderable(self) -> RenderableType:
        return self.spinner

    def transient_renderables(self) -> list[Text]:
        return [Text(f"{self.theme.transient_indent}{line.message}", style=line.color) for line in self.transient_lines]

    def done_renderable(self) -> Text:
        bullet = Text(f"{self.theme.done_marker} ", style=self.theme.done_severity_styles[self.worst_severity])
        bullet.append(self.title, style=self.theme.done_title_style)
        return bullet

    def summary_line(self, log_name: str) -> Text | None:
        message = self.summary_text(log_name)
        if message is None:
            return None
        return Text(
            f"{self.theme.transient_indent}{message}",
            style=self.theme.done_severity_styles[self.worst_severity],
        )

    def summary_text(self, log_name: str) -> str | None:
        return severity_summary(self.title, self.severity_counts, log_name)

    def to_console_group(self, active: bool, log_name: str) -> ConsoleGroup:
        return ConsoleGroup(
            title=self.title,
            active=active,
            marker_color=self.theme.done_severity_styles[self.worst_severity],
            transient_lines=tuple(ConsoleLine(line.message, line.color) for line in self.transient_lines),
            summary=self.summary_text(log_name),
        )


class SpinnerDisplay:
    def __init__(
        self,
        console: Console,
        transient_window_size: int,
        log_name: str,
        theme: ConsoleTheme | None = None,
    ) -> None:
        self._console = console
        self._transient_window_size = transient_window_size
        self._log_name = log_name
        self._theme = theme if theme is not None else ConsoleTheme()
        self._groups: list[_SpinnerGroup] = []
        self._active_group: _SpinnerGroup | None = None
        self._live_enabled = console.is_terminal
        # vertical_overflow="visible" stops Live from cropping the region once the accumulated
        # phases overflow the terminal — cropping desyncs its erase count and collapses the transient window
        self._live = (
            Live(console=console, refresh_per_second=10, transient=False, vertical_overflow="visible")
            if self._live_enabled
            else None
        )
        self._started = False

    def open_group(self, title: str) -> None:
        group = self._find_group(title)
        if group is not None:
            self._groups.remove(group)  # resuming moves the phase to the bottom, where the active spinner lives
            group.transient_lines.clear()
        else:
            group = _SpinnerGroup(
                title=title,
                spinner=Spinner(
                    self._theme.spinner_name,
                    text=Text(title, style=self._theme.active_title_style),
                    style=self._theme.spinner_style,
                ),
                transient_lines=deque(maxlen=self._transient_window_size),
                theme=self._theme,
            )
        self._groups.append(group)
        self._active_group = group
        if self._live_enabled:
            self._ensure_started()
            self._refresh()
        else:
            self._console.print(Text(title, style=self._theme.active_title_style))

    def add_line(self, message: str, level: str) -> str | None:
        if self._active_group is None:
            self.open_group("")
        self._active_group.record_severity(level)  # type: ignore[union-attr]
        if level not in _RESERVED_LEVELS:
            line_style = self._theme.transient_level_styles.get(level)
            color = line_style.to_rich_style() if line_style is not None else "white"
            self._active_group.transient_lines.append(_TransientLine(message, color))  # type: ignore[union-attr]
        if self._live_enabled:
            self._ensure_started()
            self._refresh()
        elif level not in _RESERVED_LEVELS:
            self._console.print(Text(f"{self._theme.transient_indent}{message}", style=color))
        if level in _RESERVED_LEVELS:
            return severity_summary(self._active_group.title, self._active_group.severity_counts, self._log_name)  # type: ignore[union-attr]
        return None

    def tick(self) -> None:
        if self._started:
            self._refresh()

    def close(self) -> None:
        if self._started and self._live is not None:
            self._live.update(self._final_renderable(), refresh=True)
            self._live.stop()
            self._started = False

    def snapshot(self) -> ConsoleSnapshot:
        pinned_summaries = tuple(
            ConsoleLine(summary, self._theme.done_severity_styles[group.worst_severity])
            for group in self._groups
            if (summary := group.summary_text(self._log_name)) is not None
        )
        return ConsoleSnapshot(
            groups=tuple(group.to_console_group(group is self._active_group, self._log_name) for group in self._groups),
            pinned_summaries=pinned_summaries,
            summary_pinned_at_top=self._theme.summary_pinned_at_top,
            done_marker=self._theme.done_marker,
        )

    def _find_group(self, title: str) -> _SpinnerGroup | None:
        for group in self._groups:
            if group.title == title:
                return group
        return None

    def _ensure_started(self) -> None:
        if not self._started and self._live is not None:
            self._live.start()
            self._started = True

    def _refresh(self) -> None:
        if self._live is not None:
            self._live.update(self._renderable(), refresh=True)

    def _reserved_summaries(self) -> list[Text]:
        summaries = []
        for group in self._groups:
            summary = group.summary_line(self._log_name)
            if summary is not None:
                summaries.append(summary)
        return summaries

    def _renderable(self) -> RenderableType:
        rows: list[RenderableType] = []
        if self._theme.summary_pinned_at_top:
            rows.extend(self._reserved_summaries())
        for group in self._groups:
            if group is self._active_group:
                rows.append(group.active_renderable())
                rows.extend(group.transient_renderables())
            else:
                rows.append(group.done_renderable())
            if not self._theme.summary_pinned_at_top:
                summary = group.summary_line(self._log_name)
                if summary is not None:
                    rows.append(summary)
        return Group(*rows)

    def _final_renderable(self) -> RenderableType:
        rows: list[RenderableType] = []
        if self._theme.summary_pinned_at_top:
            rows.extend(self._reserved_summaries())
        for group in self._groups:
            rows.append(group.done_renderable())
            if not self._theme.summary_pinned_at_top:
                summary = group.summary_line(self._log_name)
                if summary is not None:
                    rows.append(summary)
        return Group(*rows)
