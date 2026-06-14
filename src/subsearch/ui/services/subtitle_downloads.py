from pathlib import Path
from typing import Protocol

from PySide6.QtCore import QObject, Signal, SignalInstance

from subsearch.io import file_system
from subsearch.io.file_tracker import get_file_tracker
from subsearch.parsing import release_parser
from subsearch.runtime.config import WORKSPACE
from subsearch.runtime.models import Subtitle, SubtitleStatus
from subsearch.ui.state.tasks import TaskRunner, Worker


class DownloadFailed(Exception):
    pass


class SubtitleDownloadWorker(Worker):
    def __init__(self, subtitle: Subtitle, download_number: int, download_total: int) -> None:
        super().__init__()
        self.subtitle = subtitle
        self.download_number = download_number
        self.download_total = download_total
        self.tmp_dir: Path = WORKSPACE.download_directory
        self.subs_dir: Path = file_system.subtitle_extraction_dir(WORKSPACE.extraction_directory, subtitle.subtitle_id)

    def execute(self) -> Subtitle:
        subtitle = self.subtitle
        if release_parser.valid_filename(subtitle.subtitle_name):
            subtitle.subtitle_name = release_parser.fix_filename(subtitle.subtitle_name)
        downloaded = file_system.download_subtitle(subtitle, self.download_number, self.download_total, self.tmp_dir)
        if not downloaded:
            raise DownloadFailed(f"{subtitle.provider_name}: {subtitle.subtitle_name} is not a downloadable subtitle")
        try:
            file_system.extract_files_in_dir(self.tmp_dir, self.subs_dir)
        finally:
            get_file_tracker().delete_tracked_within(self.tmp_dir, "*.zip")
        return subtitle


class DownloadServiceProtocol(Protocol):
    started: SignalInstance
    succeeded: SignalInstance
    failed: SignalInstance

    def set_download_total(self, download_total: int) -> None: ...

    def enqueue(self, subtitle: Subtitle) -> None: ...


class SubtitleDownloadService(QObject):
    started = Signal(object)
    succeeded = Signal(object)
    failed = Signal(object, str)

    def __init__(self, task_runner: TaskRunner, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._task_runner = task_runner
        self._queue: list[Subtitle] = []
        self._active: Subtitle | None = None
        self._download_number = 1
        self._download_total = 0

    def set_download_total(self, download_total: int) -> None:
        self._download_total = download_total

    def enqueue(self, subtitle: Subtitle) -> None:
        if subtitle is self._active or subtitle in self._queue:
            return
        self._queue.append(subtitle)
        self._start_next()

    def _start_next(self) -> None:
        if self._active is not None or not self._queue:
            return
        subtitle = self._queue.pop(0)
        self._active = subtitle
        self.started.emit(subtitle)
        worker = SubtitleDownloadWorker(subtitle, self._download_number, self._download_total)
        worker.finished.connect(self._on_worker_finished)
        worker.failed.connect(self._on_worker_failed)
        self._task_runner.submit(worker)

    def _on_worker_finished(self, subtitle: Subtitle) -> None:
        subtitle.status = SubtitleStatus.MANUALLY_DOWNLOADED
        self._download_number += 1
        self._active = None
        self.succeeded.emit(subtitle)
        self._start_next()

    def _on_worker_failed(self, message: str) -> None:
        subtitle = self._active
        self._active = None
        if subtitle is not None:
            subtitle.status = SubtitleStatus.DOWNLOAD_FAILED
            self.failed.emit(subtitle, message)
        self._start_next()
