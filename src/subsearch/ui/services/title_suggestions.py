from PySide6.QtCore import QObject, Signal

from subsearch.parsing.imdb_lookup import TitleSuggestion, find_title_suggestions
from subsearch.ui.state.tasks import TaskRunner, Worker


class TitleSuggestionWorker(Worker):
    def __init__(self, typed_term: str) -> None:
        super().__init__()
        self.typed_term = typed_term

    def execute(self) -> list[TitleSuggestion]:
        return find_title_suggestions(self.typed_term)


class TitleSuggestionService(QObject):
    suggestions_ready = Signal(str, list)
    lookup_failed = Signal(str)

    def __init__(self, task_runner: TaskRunner, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._task_runner = task_runner
        self._latest_term = ""

    def request(self, typed_term: str) -> None:
        self._latest_term = typed_term
        worker = TitleSuggestionWorker(typed_term)
        worker.finished.connect(lambda suggestions, term=typed_term: self._on_finished(term, suggestions))
        worker.failed.connect(self.lookup_failed)
        self._task_runner.submit(worker)

    def _on_finished(self, typed_term: str, suggestions: list[TitleSuggestion]) -> None:
        if typed_term != self._latest_term:
            # a newer request superseded this one; drop the stale result
            return
        self.suggestions_ready.emit(typed_term, suggestions)
