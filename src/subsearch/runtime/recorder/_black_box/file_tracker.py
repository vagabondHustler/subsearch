from pathlib import Path

from subsearch.io import file_system
from subsearch.runtime.config import APP_PATHS
from subsearch.runtime.recorder.config import LogLevel
from subsearch.runtime.recorder.standard_in import capture

TEMP_DIRECTORY_NAME = APP_PATHS.tmp_dir.name


class FileTracker:
    """Registry of paths the app created; enables safe deletion and crash recovery.

    Persists the tracked set to a JSON manifest so it survives process restarts.
    Only paths explicitly added via ``track()`` are ever deleted by this class.
    """

    def __init__(self, manifest_path: Path) -> None:
        self.manifest_path = manifest_path
        self.tracked_paths: set[str] = {str(path) for path in file_system.read_json_list(manifest_path)}

    def _save_manifest(self) -> None:
        file_system.write_json_list(self.manifest_path, sorted(self.tracked_paths))

    def track(self, path: Path) -> None:
        """Register ``path`` as app-owned and persist the manifest."""
        capture(f"Tracking {path}", level=LogLevel.DEBUG)
        self.tracked_paths.add(str(path.resolve()))
        self._save_manifest()

    def is_tracked(self, path: Path) -> bool:
        """Return ``True`` if ``path`` is in the tracked set."""
        return str(path.resolve()) in self.tracked_paths

    def forget(self, path: Path) -> None:
        """Remove ``path`` from the tracked set without deleting the file."""
        capture(f"Released {path}", level=LogLevel.DEBUG)
        self.tracked_paths.discard(str(path.resolve()))
        self._save_manifest()

    def delete_if_tracked(self, path: Path) -> bool:
        """Delete ``path`` and untrack it; returns ``False`` and skips if not tracked."""
        if not self.is_tracked(path):
            if path.exists():
                capture(f"Refusing to delete untracked path {path}", level=LogLevel.DEBUG)
            return False
        kind = "directory" if path.is_dir() else "file"
        file_system.delete_path(path)
        capture(f"Removing {kind}: {path}")
        self.forget(path)
        return True

    def delete_tracked_within(self, directory: Path, pattern: str = "*") -> None:
        """Delete every tracked file inside ``directory`` matching ``pattern``."""
        if not directory.is_dir():
            return
        for file in directory.glob(pattern):
            if file.is_file() and self.is_tracked(file):
                self.delete_if_tracked(file)

    def reclaim_after_crash(self) -> None:
        """Purge stale manifest entries and delete leftover temp paths from a prior crash."""
        for tracked in sorted(self.tracked_paths, reverse=True):
            path = Path(tracked)
            if not path.exists():
                capture(f"Discarding stale tracked path {path}", level=LogLevel.DEBUG)
                self.tracked_paths.discard(tracked)
            elif self._is_temp_path(path):
                capture(f"Reclaiming leftover temp path {path}", level=LogLevel.DEBUG)
                file_system.delete_path(path)
                self.tracked_paths.discard(tracked)
        self._save_manifest()

    @staticmethod
    def _is_temp_path(path: Path) -> bool:
        return TEMP_DIRECTORY_NAME in (path.name, *(parent.name for parent in path.parents))
