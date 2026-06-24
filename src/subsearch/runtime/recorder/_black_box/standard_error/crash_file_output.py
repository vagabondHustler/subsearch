import threading
from pathlib import Path

from subsearch.runtime.recorder.config import SESSION_SEPARATOR


class CrashFileOutput:
    def __init__(self, path: Path, max_bytes: int, clear_every_runs: int) -> None:
        self._path = path
        self._max_bytes = max_bytes
        self._clear_every_runs = clear_every_runs
        self._lock = threading.Lock()

    def write_session(self, session: str) -> None:
        if not session.strip():
            return
        with self._lock:
            self._ensure_parent()
            if self._should_clear():
                self._path.write_text("", encoding="utf-8")
            self._append(f"{SESSION_SEPARATOR}\n{session}\n")
            self._cap_size()

    def _ensure_parent(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)

    def _should_clear(self) -> bool:
        return self._session_count() % self._clear_every_runs == 0

    def _session_count(self) -> int:
        if not self._path.exists():
            return 0
        return self._path.read_text(encoding="utf-8", errors="replace").count(SESSION_SEPARATOR)

    def _append(self, text: str) -> None:
        with self._path.open("a", encoding="utf-8") as crash_file:
            crash_file.write(text)

    def _cap_size(self) -> None:
        if self._path.stat().st_size <= self._max_bytes:
            return
        contents = self._path.read_bytes()[-self._max_bytes :]
        self._path.write_bytes(contents)
