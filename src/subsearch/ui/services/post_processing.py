from pathlib import Path
from typing import Protocol

from PySide6.QtCore import QObject, Signal, SignalInstance

from subsearch.io import file_system
from subsearch.runtime.config.constants import VIDEO_FILE
from subsearch.runtime.logging.logger import log
from subsearch.runtime.models.model import Subtitle
from subsearch.ui.state.store import SettingsStore
from subsearch.ui.state.tasks import TaskRunner, Worker


class _PostProcessWorker(Worker):
    def __init__(self, rename: bool, store: SettingsStore) -> None:
        super().__init__()
        self._rename = rename
        self._store = store

    def execute(self) -> object:
        target_path = self._resolve_target_path()
        log.event("post_processing_started", destination=target_path)
        extracted_count = file_system.extract_files_in_dir(
            VIDEO_FILE.download_directory, VIDEO_FILE.extraction_directory
        )
        if self._rename:
            renamed = file_system.autoload_rename(VIDEO_FILE.filename, VIDEO_FILE.extraction_directory)
            file_system.move_and_replace(renamed, target_path)
            moved_count = 1 if (target_path / renamed.name).exists() else 0
        else:
            moved_count = file_system.move_all(VIDEO_FILE.extraction_directory, target_path)
        if extracted_count == 0 or moved_count == 0:
            log.event(
                "post_processing_no_files",
                level="warning",
                destination=target_path,
                extracted=extracted_count,
                moved=moved_count,
            )
        log.event("post_processing_completed", destination=target_path, extracted=extracted_count, moved=moved_count)
        return None

    def _resolve_target_path(self) -> Path:
        target = str(self._store.read("paths.video_file_directory"))
        resolution = str(self._store.read("paths.path_resolution"))
        create = bool(self._store.read("paths.create_missing_directory"))
        return file_system.create_path_from_string(target, resolution, VIDEO_FILE.file_directory, create)


class PostProcessingServiceProtocol(Protocol):
    succeeded: SignalInstance
    failed: SignalInstance

    def unpack_and_move(self, store: SettingsStore) -> None: ...

    def unpack_rename_and_place(self, store: SettingsStore) -> None: ...


class PostProcessingService(QObject):
    succeeded = Signal()
    failed = Signal(str)

    def __init__(self, task_runner: TaskRunner, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._task_runner = task_runner

    def unpack_and_move(self, store: SettingsStore) -> None:
        self._run(rename=False, store=store)

    def unpack_rename_and_place(self, store: SettingsStore) -> None:
        self._run(rename=True, store=store)

    def _run(self, rename: bool, store: SettingsStore) -> None:
        worker = _PostProcessWorker(rename=rename, store=store)
        worker.finished.connect(lambda _: self.succeeded.emit())
        worker.failed.connect(self._on_failed)
        self._task_runner.submit(worker)

    def _on_failed(self, reason: str) -> None:
        log.event("post_processing_failed", level="error", reason=reason)
        self.failed.emit(reason)
