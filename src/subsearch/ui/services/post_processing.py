from pathlib import Path
from typing import Protocol

from PySide6.QtCore import QObject, Signal, SignalInstance

from subsearch.io import file_system
from subsearch.runtime.config import SEARCH_SUBJECT, WORKSPACE
from subsearch.runtime.config.defaults import ConfigKey
from subsearch.runtime.logging.events import LogEvent
from subsearch.runtime.logging.logger import log
from subsearch.runtime.models import Subtitle
from subsearch.ui.state.store import SettingsStore
from subsearch.ui.state.tasks import TaskRunner, Worker


class _PostProcessWorker(Worker):
    def __init__(self, rename: bool, store: SettingsStore, subtitle: Subtitle) -> None:
        super().__init__()
        self._rename = rename
        self._store = store
        self._subtitle_id = subtitle.subtitle_id
        self._subtitle_name = subtitle.subtitle_name
        self._download_dir = WORKSPACE.download_directory
        self._extraction_dir = WORKSPACE.extraction_directory
        self.delivered_directory = ""

    def execute(self) -> int:
        extracted_count = self._unpack_subtitle()
        if extracted_count == 0:
            extracted_count = self._count_already_placed()
        if extracted_count == 0:
            self._log_no_files(self._extraction_dir, extracted_count)
            return 0
        if self._rename:
            return self._rename_and_place()
        log.event(
            LogEvent.POST_PROCESSING_COMPLETED,
            destination=self._extraction_dir,
            source=self._download_dir,
            moved=extracted_count,
        )
        self.delivered_directory = str(self._extraction_dir)
        return extracted_count

    def _unpack_subtitle(self) -> int:
        return file_system.extract_subtitle_by_id(self._subtitle_id, self._download_dir, self._extraction_dir)

    def _count_already_placed(self) -> int:
        return file_system.count_raw_subtitles_by_name(self._subtitle_name, self._extraction_dir)

    def _rename_and_place(self) -> int:
        target_path = self._resolve_target_path()
        renamed = file_system.autoload_rename(SEARCH_SUBJECT.search_term, self._extraction_dir)
        file_system.move_and_replace(renamed, target_path)
        placed = (target_path / renamed.name).exists()
        if not placed:
            self._log_no_files(target_path, 0)
            return 0
        log.event(LogEvent.POST_PROCESSING_COMPLETED, destination=target_path, source=self._extraction_dir, moved=1)
        self.delivered_directory = str(target_path)
        return 1

    def _log_no_files(self, destination: Path, moved: int) -> None:
        log.event(
            LogEvent.POST_PROCESSING_NO_FILES,
            level="warning",
            destination=destination,
            source=self._download_dir,
            moved=moved,
        )

    def _resolve_target_path(self) -> Path:
        target = str(self._store.read(ConfigKey.PATHS_VIDEO_FILE_DIRECTORY))
        resolution = str(self._store.read(ConfigKey.PATHS_PATH_RESOLUTION))
        create = bool(self._store.read(ConfigKey.PATHS_CREATE_MISSING_DIRECTORY))
        return file_system.create_path_from_string(target, resolution, WORKSPACE.file_directory, create)


class PostProcessingServiceProtocol(Protocol):
    succeeded: SignalInstance
    failed: SignalInstance

    def unpack_and_move(self, store: SettingsStore, subtitle: Subtitle) -> None: ...

    def unpack_rename_and_place(self, store: SettingsStore, subtitle: Subtitle) -> None: ...


class PostProcessingService(QObject):
    succeeded = Signal(str)
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
        worker.finished.connect(lambda moved: self._on_finished(worker, moved))
        worker.failed.connect(self._on_failed)
        self._task_runner.submit(worker)

    def _on_finished(self, worker: "_PostProcessWorker", moved: object) -> None:
        if isinstance(moved, int) and moved > 0:
            self.succeeded.emit(worker.delivered_directory)
        else:
            self.failed.emit("No subtitles were delivered to the destination")

    def _on_failed(self, reason: str) -> None:
        log.event(LogEvent.POST_PROCESSING_FAILED, level="error", reason=reason)
        self.failed.emit(reason)
