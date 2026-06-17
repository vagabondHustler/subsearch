import json
import shutil
from pathlib import Path

from subsearch.runtime.config import APP_PATHS
from subsearch.runtime.logging.events import LogEvent
from subsearch.runtime.logging.logger import log

TEMP_DIRECTORY_NAME = "tmp_subsearch"


class FileTracker:
    def __init__(self, manifest_path: Path) -> None:
        self.manifest_path = manifest_path
        self.tracked_paths: set[str] = self._load_manifest()

    def _load_manifest(self) -> set[str]:
        if not self.manifest_path.exists():
            return set()
        try:
            return set(json.loads(self.manifest_path.read_text(encoding="utf-8")))
        except (json.JSONDecodeError, OSError):
            log.event(LogEvent.TRACKER_MANIFEST_UNREADABLE, level="warning", path=self.manifest_path)
            return set()

    def _save_manifest(self) -> None:
        self.manifest_path.parent.mkdir(parents=True, exist_ok=True)
        self.manifest_path.write_text(json.dumps(sorted(self.tracked_paths)), encoding="utf-8")

    def track(self, path: Path) -> None:
        log.event(LogEvent.TRACKER_TRACKING, level="debug", path=path)
        self.tracked_paths.add(str(path.resolve()))
        self._save_manifest()

    def is_tracked(self, path: Path) -> bool:
        return str(path.resolve()) in self.tracked_paths

    def forget(self, path: Path) -> None:
        log.event(LogEvent.TRACKER_RELEASED, level="debug", path=path)
        self.tracked_paths.discard(str(path.resolve()))
        self._save_manifest()

    def delete_if_tracked(self, path: Path) -> bool:
        if not self.is_tracked(path):
            if path.exists():
                log.event(LogEvent.TRACKER_REFUSING_UNTRACKED, level="debug", path=path)
            return False
        if path.is_dir():
            shutil.rmtree(path, ignore_errors=True)
        elif path.exists():
            path.unlink(missing_ok=True)
        log.event(LogEvent.REMOVE, src=path)
        self.forget(path)
        return True

    def delete_tracked_within(self, directory: Path, pattern: str = "*") -> None:
        if not directory.is_dir():
            return
        for file in directory.glob(pattern):
            if file.is_file() and self.is_tracked(file):
                self.delete_if_tracked(file)

    def reclaim_after_crash(self) -> None:
        for tracked in sorted(self.tracked_paths, reverse=True):
            path = Path(tracked)
            if not path.exists():
                log.event(LogEvent.TRACKER_DISCARDING_STALE, level="debug", path=path)
                self.tracked_paths.discard(tracked)
            elif self._is_temp_path(path):
                log.event(LogEvent.TRACKER_RECLAIMING, level="debug", path=path)
                if path.is_dir():
                    shutil.rmtree(path, ignore_errors=True)
                else:
                    path.unlink(missing_ok=True)
                self.tracked_paths.discard(tracked)
        self._save_manifest()

    @staticmethod
    def _is_temp_path(path: Path) -> bool:
        return TEMP_DIRECTORY_NAME in (path.name, *(parent.name for parent in path.parents))


_active_file_tracker: FileTracker | None = None


def get_file_tracker() -> FileTracker:
    global _active_file_tracker
    if _active_file_tracker is None:
        _active_file_tracker = FileTracker(APP_PATHS.appdata_subsearch / "tracked_files.json")
    return _active_file_tracker
