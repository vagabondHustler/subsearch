from PySide6.QtCore import QObject

from subsearch.io import windows_registry
from subsearch.ui.state.tasks import TaskRunner, Worker


class RegistryWorker(Worker):
    def execute(self) -> None:
        windows_registry.reconcile_shell_integration()


class ShellIntegrationService(QObject):
    def __init__(self, task_runner: TaskRunner, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._task_runner = task_runner

    def reconcile(self) -> None:
        self._task_runner.submit(RegistryWorker())
