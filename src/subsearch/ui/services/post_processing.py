from pathlib import Path
from typing import Protocol

from PySide6.QtCore import QObject, Signal, SignalInstance

from subsearch.io import file_system
from subsearch.runtime.config import SEARCH_SUBJECT, WORKSPACE
from subsearch.runtime.logging.logger import log
from subsearch.runtime.models import Subtitle
from subsearch.ui.state.store import SettingsStore
from subsearch.ui.state.tasks import TaskRunner, Worker


class _PostProcessWorker(Worker):
    def __init__(self, rename: bool, store: SettingsStore, subtitle: Subtitle) -> None:
        super().__init__()
        self._rename = rename
        self._store = store
        self._source_dir = file_system.subtitle_extraction_dir(WORKSPACE.extraction_directory, subtitle.subtitle_id)

    def execute(self) -> int:
        target_path = self._resolve_target_path()
        log.event("post_processing_started", destination=target_path, source=self._source_dir)
        if self._rename:
            renamed = file_system.autoload_rename(SEARCH_SUBJECT.search_term, self._source_dir)
            file_system.move_and_replace(renamed, target_path)
            moved_count = 1 if (target_path / renamed.name).exists() else 0
        else:
            moved_count = file_system.move_all(self._source_dir, target_path)
        delivered_count = self._delivered_count(moved_count, target_path)
        if delivered_count == 0:
            log.event(
                "post_processing_no_files",
                level="warning",
                destination=target_path,
                source=self._source_dir,
                moved=moved_count,
            )
        log.event("post_processing_completed", destination=target_path, source=self._source_dir, moved=moved_count)
        return delivered_count

    def _delivered_count(self, moved_count: int, target_path: Path) -> int:
        if moved_count > 0:
            return moved_count
        if self._source_dir.resolve() == target_path.resolve():
            return file_system.count_subtitle_files(target_path)
        return 0

    def _resolve_target_path(self) -> Path:
        target = str(self._store.read("paths.video_file_directory"))
        resolution = str(self._store.read("paths.path_resolution"))
        create = bool(self._store.read("paths.create_missing_directory"))
        return file_system.create_path_from_string(target, resolution, WORKSPACE.file_directory, create)


class PostProcessingServiceProtocol(Protocol):
    succeeded: SignalInstance
    failed: SignalInstance

    def unpack_and_move(self, store: SettingsStore, subtitle: Subtitle) -> None: ...

    def unpack_rename_and_place(self, store: SettingsStore, subtitle: Subtitle) -> None: ...


class PostProcessingService(QObject):
    succeeded = Signal(int)
    failed = Signal(str)

    def __init__(self, task_runner: TaskRunner, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._task_runner = task_runner

    def unpack_and_move(self, store: SettingsStore, subtitle: Subtitle) -> None:
        self._run(rename=False, store=store, subtitle=subtitle)

    def unpack_rename_and_place(self, store: SettingsStore, subtitle: Subtitle) -> None:
        self._run(rename=True, store=store, subtitle=subtitle)

    def _run(self, rename: bool, store: SettingsStore, subtitle: Subtitle) -> None:
        worker = _PostProcessWorker(rename=rename, store=store, subtitle=subtitle)
        worker.finished.connect(self._on_finished)
        worker.failed.connect(self._on_failed)
        self._task_runner.submit(worker)

    def _on_finished(self, delivered_count: object) -> None:
        if isinstance(delivered_count, int) and delivered_count > 0:
            self.succeeded.emit(delivered_count)
        else:
            self.failed.emit("No subtitles were delivered to the destination")

    def _on_failed(self, reason: str) -> None:
        log.event("post_processing_failed", level="error", reason=reason)
        self.failed.emit(reason)
