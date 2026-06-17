from PySide6.QtCore import QObject, QThread, Signal

from subsearch.runtime.logging.events import LogEvent
from subsearch.runtime.logging.logger import log


class Worker(QObject):
    finished = Signal(object)
    failed = Signal(str)

    def execute(self) -> object:
        raise NotImplementedError

    def run(self) -> None:
        try:
            self.finished.emit(self.execute())
        except Exception as error:
            log.event(LogEvent.TASK_FAILED, level="error", reason=str(error))
            self.failed.emit(str(error))


class TaskRunner(QObject):
    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._active: list[tuple[QThread, Worker]] = []

    def submit(self, worker: Worker) -> None:
        thread = QThread(self)
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        worker.finished.connect(thread.quit)
        worker.failed.connect(thread.quit)
        # Bound-method receiver makes this a queued connection, so reaping runs
        # on the TaskRunner's thread instead of inside the dying worker thread.
        thread.finished.connect(self._reap_finished_threads)
        self._active.append((thread, worker))
        thread.start()

    def _reap_finished_threads(self) -> None:
        still_active: list[tuple[QThread, Worker]] = []
        for thread, worker in self._active:
            if thread.isFinished():
                thread.wait()
                worker.deleteLater()
                thread.deleteLater()
            else:
                still_active.append((thread, worker))
        self._active = still_active

    def shutdown(self) -> None:
        for thread, worker in self._active:
            thread.quit()
            thread.wait()
            worker.deleteLater()
            thread.deleteLater()
        self._active.clear()
