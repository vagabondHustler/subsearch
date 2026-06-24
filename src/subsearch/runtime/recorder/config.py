from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Callable

LOG_FORMAT = "%(asctime)s %(levelname)-8s %(module)s:%(lineno)d %(message)s"
LOG_DATE_FORMAT = "%H:%M:%S"
LOG_MAX_BYTES = 1_000_000
CRASH_CLEAR_EVERY_RUNS = 5
SESSION_SEPARATOR = "\x1c"
TRANSIENT_WINDOW_SIZE = 3
TICK_SECONDS = 0.1


class LogLevel(StrEnum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    PHASE = "phase"


@dataclass(frozen=True, slots=True)
class ConsoleLine:
    """One transient line of a phase, carrying the hex color the terminal renders it in."""

    text: str
    color: str


@dataclass(frozen=True, slots=True)
class ConsoleGroup:
    """A phase as both consoles draw it: a spinner while active, a done-marker once finished."""

    title: str
    active: bool
    marker_color: str
    transient_lines: tuple[ConsoleLine, ...]
    summary: str | None


@dataclass(frozen=True, slots=True)
class ConsoleSnapshot:
    """The whole console box at one instant — the single model both consoles render.

    The terminal draws it through ``rich``; the UI console rebuilds its widget from the
    same fields, so the two stay byte-identical.
    """

    groups: tuple[ConsoleGroup, ...]
    pinned_summaries: tuple[ConsoleLine, ...]
    summary_pinned_at_top: bool
    done_marker: str


@dataclass(frozen=True, slots=True)
class RecorderConfig:
    """Immutable configuration handed to ``recorder.init()``.

    ``console_outputs`` is a tuple of callables that each receive a ``ConsoleSnapshot`` —
    the full console box at one instant. Plug in the UI console here; the terminal renders
    itself directly. Both consume the same snapshot, so they stay byte-identical.

    ``start_perf_counter`` is the process start reading from ``time.perf_counter()``;
    when set, ``shutdown()`` closes with an "Exiting" phase reporting elapsed run time.
    """

    log_file_path: Path
    crash_file_path: Path
    console_outputs: tuple[Callable[[ConsoleSnapshot], None], ...] = field(default_factory=tuple)
    start_perf_counter: float | None = None
    log_max_bytes: int = LOG_MAX_BYTES
    crash_clear_every_runs: int = CRASH_CLEAR_EVERY_RUNS
    transient_window_size: int = TRANSIENT_WINDOW_SIZE
    tick_seconds: float = TICK_SECONDS
