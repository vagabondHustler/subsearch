from PySide6.QtCore import QObject, QThread, Signal

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
            log.error(str(error))
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
        thread.finished.connect(
            lambda finished_thread=thread, finished_worker=worker: self._discard(finished_thread, finished_worker)
        )
        self._active.append((thread, worker))
        thread.start()

    def _discard(self, thread: QThread, worker: Worker) -> None:
        self._active = [
            (active_thread, active_worker)
            for active_thread, active_worker in self._active
            if active_thread is not thread
        ]
        worker.deleteLater()
        thread.deleteLater()

    def shutdown(self) -> None:
        for thread, _worker in list(self._active):
            thread.quit()
            thread.wait()
        self._active.clear()
