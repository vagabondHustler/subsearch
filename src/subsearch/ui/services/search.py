from typing import Protocol

from subsearch.runtime.models import SearchOutcome
from subsearch.ui.state.tasks import Worker


class SearchJobProtocol(Protocol):
    def execute(self) -> SearchOutcome: ...


class SearchJobWorker(Worker):
    def __init__(self, search_job: SearchJobProtocol) -> None:
        super().__init__()
        self._search_job = search_job

    def execute(self) -> SearchOutcome:
        return self._search_job.execute()
