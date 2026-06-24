from typing import TYPE_CHECKING, Any

from subsearch.runtime.recorder.config import (
    ConsoleGroup,
    ConsoleLine,
    ConsoleSnapshot,
    LogLevel,
    RecorderConfig,
)
from subsearch.runtime.recorder.console_theme import ConsoleTheme, Emphasis, LineStyle
from subsearch.runtime.recorder.standard_in import (
    capture,
    flush_crash,
    get_file_tracker,
    init,
    phase,
    shutdown,
)

if TYPE_CHECKING:
    from subsearch.runtime.recorder._black_box.file_tracker import FileTracker

__all__ = [
    "ConsoleGroup",
    "ConsoleLine",
    "ConsoleSnapshot",
    "ConsoleTheme",
    "Emphasis",
    "FileTracker",
    "LineStyle",
    "LogLevel",
    "RecorderConfig",
    "capture",
    "flush_crash",
    "get_file_tracker",
    "init",
    "phase",
    "shutdown",
]


def __getattr__(name: str) -> Any:
    # FileTracker pulls in io.file_system, which imports back from this package; resolve it
    # lazily so importing the recorder package doesn't form a circular import at module load.
    if name == "FileTracker":
        from subsearch.runtime.recorder._black_box.file_tracker import FileTracker

        return FileTracker
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
