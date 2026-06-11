from pathlib import Path
from typing import Protocol

from PySide6.QtCore import QObject, Signal, SignalInstance

from subsearch.io import file_system
from subsearch.parsing import release_parser
from subsearch.runtime.config.constants import VIDEO_FILE
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
        file_system.extract_files_in_dir(VIDEO_FILE.tmp_dir, VIDEO_FILE.subs_dir)
        if self._rename:
            renamed = file_system.autoload_rename(VIDEO_FILE.filename, VIDEO_FILE.subs_dir, ".srt")
            file_system.move_and_replace(renamed, target_path)
        else:
            file_system.move_all(VIDEO_FILE.subs_dir, target_path)
        return None

    def _resolve_target_path(self) -> Path:
        if self._store.read("download_manager.use_post_processing_target"):
            target = str(self._store.read("post_processing.target_path"))
            resolution = str(self._store.read("post_processing.path_resolution"))
            create = bool(self._store.read("post_processing.create_missing_folder"))
        else:
            target = str(self._store.read("download_manager.target_path"))
            resolution = release_parser.detect_path_resolution(target)
            create = True
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
        worker = _PostProcessWorker(rename=False, store=store)
        worker.finished.connect(lambda _: self.succeeded.emit())
        worker.failed.connect(self.failed.emit)
        self._task_runner.submit(worker)

    def unpack_rename_and_place(self, store: SettingsStore) -> None:
        worker = _PostProcessWorker(rename=True, store=store)
        worker.finished.connect(lambda _: self.succeeded.emit())
        worker.failed.connect(self.failed.emit)
        self._task_runner.submit(worker)
