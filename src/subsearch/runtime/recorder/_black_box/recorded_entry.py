from dataclasses import dataclass

from subsearch.runtime.recorder.config import LogLevel


@dataclass(frozen=True, slots=True)
class RecordedEntry:
    lines: tuple[str, ...]
    level: LogLevel
    module: str
    line_number: int
    captured_at: float

    @property
    def message(self) -> str:
        return "\n".join(self.lines)
