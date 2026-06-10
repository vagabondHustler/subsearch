from typing import Callable

from PySide6.QtCore import QObject

from subsearch.io import windows_registry
from subsearch.ui.state.tasks import TaskRunner, Worker


class RegistryWorker(Worker):
    def __init__(self, operation: Callable[[], None]) -> None:
        super().__init__()
        self._operation = operation

    def execute(self) -> None:
        self._operation()


class ShellIntegrationService(QObject):
    def __init__(self, task_runner: TaskRunner, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._task_runner = task_runner

    def set_context_menu_enabled(self, enabled: bool) -> None:
        operation = windows_registry.add_context_menu if enabled else windows_registry.del_context_menu
        self._task_runner.submit(RegistryWorker(operation))

    def refresh_registry_value(self, key: str) -> None:
        self._task_runner.submit(RegistryWorker(lambda: windows_registry.write_registry_value_by_key(key)))
