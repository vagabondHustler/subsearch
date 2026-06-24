from pathlib import Path

from subsearch.runtime.recorder.config import SESSION_SEPARATOR


class RotatingLogFileOutput:
    def __init__(self, path: Path, max_bytes: int) -> None:
        self._path = path
        self._max_bytes = max_bytes
        self._session_started = False

    def write(self, text: str) -> None:
        self._ensure_parent()
        self._start_session_once()
        self._append(text + "\n")
        self._cap_size()

    def tick(self) -> None:
        return None

    def close(self) -> None:
        return None

    def _ensure_parent(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)

    def _start_session_once(self) -> None:
        if self._session_started:
            return
        self._append(f"{SESSION_SEPARATOR}\n")
        self._session_started = True

    def _append(self, text: str) -> None:
        with self._path.open("a", encoding="utf-8") as log_file:
            log_file.write(text)

    def _cap_size(self) -> None:
        if self._path.stat().st_size <= self._max_bytes:
            return
        contents = self._path.read_bytes()[-self._max_bytes :]
        self._path.write_bytes(contents)
