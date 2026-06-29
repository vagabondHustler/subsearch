from pathlib import Path
from typing import Protocol

from PySide6.QtCore import QObject, Signal, SignalInstance

from subsearch.io import file_system
from subsearch.parsing import release_parser
from subsearch.runtime.config import WORKSPACE
from subsearch.runtime.models import Subtitle, SubtitleStatus
from subsearch.runtime.recorder import LogLevel, capture, phase
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

    def execute(self) -> Subtitle:
        subtitle = self.subtitle
        if release_parser.valid_filename(subtitle.subtitle_name):
            subtitle.subtitle_name = release_parser.fix_filename(subtitle.subtitle_name)
        downloaded = file_system.download_subtitle(subtitle, self.download_number, self.download_total, self.tmp_dir)
        if downloaded is None:
            raise DownloadFailed(f"{subtitle.provider_name}: {subtitle.subtitle_name} is not a downloadable subtitle")
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
        self._processing_announced = False

    def set_download_total(self, download_total: int) -> None:
        self._download_total = download_total

    def enqueue(self, subtitle: Subtitle) -> None:
        if subtitle is self._active or subtitle in self._queue:
            return
        self._queue.append(subtitle)
        self._start_next()

    def _start_next(self) -> None:
        if self._active is not None:
            return
        if not self._queue:
            self._end_processing_phase()
            return
        self._begin_processing_phase()
        subtitle = self._queue.pop(0)
        self._active = subtitle
        self.started.emit(subtitle)
        worker = SubtitleDownloadWorker(subtitle, self._download_number, self._download_total)
        worker.finished.connect(self._on_worker_finished)
        worker.failed.connect(self._on_worker_failed)
        self._task_runner.submit(worker)

    def _begin_processing_phase(self) -> None:
        # Mirror the automatic flow: a burst of downloads is announced once,
        # opened after search (downloads only start once results exist).
        if self._processing_announced:
            return
        phase("Processing subtitles")
        self._processing_announced = True

    def _end_processing_phase(self) -> None:
        self._processing_announced = False

    def _on_worker_finished(self, subtitle: Subtitle) -> None:
        subtitle.status = SubtitleStatus.MANUAL_DOWNLOAD
        self._download_number += 1
        self._active = None
        self.succeeded.emit(subtitle)
        self._start_next()

    def _on_worker_failed(self, message: str) -> None:
        subtitle = self._active
        self._active = None
        if subtitle is not None:
            subtitle.status = SubtitleStatus.DOWNLOAD_FAILED
            capture(f"Download failed: {message}", level=LogLevel.ERROR)
            self.failed.emit(subtitle, message)
        self._start_next()
