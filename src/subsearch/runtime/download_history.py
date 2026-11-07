from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

from subsearch.io import file_system
from subsearch.runtime.config import APP_PATHS

_RETENTION_DAYS = 7
_RETENTION_RUNS = 10


class DownloadRecord:
    def __init__(self, recorded_on: str, content_hash: str, url: str, path: str, run: int) -> None:
        self.recorded_on = recorded_on
        self.content_hash = content_hash
        self.url = url
        self.path = path
        self.run = run

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DownloadRecord":
        return cls(
            recorded_on=data["date"],
            content_hash=data["hash"],
            url=data["url"],
            path=data["path"],
            run=data.get("run", 0),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "date": self.recorded_on,
            "hash": self.content_hash,
            "url": self.url,
            "path": self.path,
            "run": self.run,
        }


class DownloadHistory:
    """Persisted record of kept automatic downloads, used to skip duplicates.

    Holds the dedupe policy state — which URLs/hashes are already on disk and the
    paths queued for deletion. ``io`` moves the bytes; this class decides.
    """

    def __init__(self, history_path: Path) -> None:
        self._history_path = history_path
        data = self._load()
        self._records = [DownloadRecord.from_dict(entry) for entry in data.get("download_history", [])]
        self._pending_deletion: list[str] = list(data.get("pending_deletion", []))
        self._run_count: int = data.get("run_count", 0)

    def _load(self) -> dict[str, Any]:
        return file_system.read_json_dict(self._history_path)

    def _save(self) -> None:
        file_system.write_json_dict(
            self._history_path,
            {
                "pending_deletion": self._pending_deletion,
                "download_history": [record.to_dict() for record in self._records],
                "run_count": self._run_count,
            },
        )

    @property
    def run_count(self) -> int:
        return self._run_count

    def was_downloaded_url(self, url: str) -> bool:
        return any(record.url == url for record in self._records)

    def was_downloaded_hash(self, content_hash: str) -> bool:
        return any(record.content_hash == content_hash for record in self._records)

    def record(self, content_hash: str, url: str, path: Path) -> None:
        self._records.append(
            DownloadRecord(
                recorded_on=date.today().isoformat(),
                content_hash=content_hash,
                url=url,
                path=str(path),
                run=self._run_count,
            )
        )
        self._save()

    def mark_pending_deletion(self, path: Path) -> None:
        resolved = str(path)
        if resolved not in self._pending_deletion:
            self._pending_deletion.append(resolved)
            self._save()

    def take_pending_deletion(self) -> list[Path]:
        paths = [Path(entry) for entry in self._pending_deletion]
        self._pending_deletion = []
        self._save()
        return paths

    def increment_run_count(self) -> None:
        self._run_count += 1
        self._save()

    def prune(self, days: int = _RETENTION_DAYS, runs: int = _RETENTION_RUNS) -> None:
        oldest_allowed_date = (datetime.now() - timedelta(days=days)).date()
        oldest_allowed_run = self._run_count - runs
        self._records = [
            record
            for record in self._records
            if date.fromisoformat(record.recorded_on) >= oldest_allowed_date and record.run > oldest_allowed_run
        ]
        self._save()


_download_history: DownloadHistory | None = None


def get_download_history() -> DownloadHistory:
    global _download_history
    if _download_history is None:
        _download_history = DownloadHistory(APP_PATHS.appdata_subsearch / "download_history.json")
    return _download_history
