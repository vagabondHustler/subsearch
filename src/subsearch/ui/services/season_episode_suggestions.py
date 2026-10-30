from PySide6.QtCore import QObject, Signal

from subsearch.parsing.imdb_lookup import (
    EpisodeSuggestion,
    SeasonSuggestion,
    find_episode_suggestions,
    find_season_suggestions,
)
from subsearch.ui.state.tasks import TaskRunner, Worker


class SeasonSuggestionWorker(Worker):
    def __init__(self, title: str, imdb_id: str) -> None:
        super().__init__()
        self.title = title
        self.imdb_id = imdb_id

    def execute(self) -> list[SeasonSuggestion]:
        from subsearch.parsing.gestdown_lookup import GestdownLookup

        return GestdownLookup().find_season_suggestions(self.title) or find_season_suggestions(self.imdb_id)


class EpisodeSuggestionWorker(Worker):
    def __init__(self, title: str, imdb_id: str, season: int, language_name: str) -> None:
        super().__init__()
        self.title = title
        self.imdb_id = imdb_id
        self.season = season
        self.language_name = language_name

    def execute(self) -> list[EpisodeSuggestion]:
        from subsearch.parsing.gestdown_lookup import GestdownLookup

        gestdown = GestdownLookup().find_episode_suggestions(self.title, self.season, self.language_name)
        return gestdown or find_episode_suggestions(self.imdb_id, self.season)


class SeasonEpisodeSuggestionService(QObject):
    seasons_ready = Signal(list)
    episodes_ready = Signal(int, list)
    lookup_failed = Signal(str)

    def __init__(self, task_runner: TaskRunner, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._task_runner = task_runner

    def request_seasons(self, title: str, imdb_id: str) -> None:
        worker = SeasonSuggestionWorker(title, imdb_id)
        worker.finished.connect(lambda seasons: self.seasons_ready.emit(seasons))
        worker.failed.connect(self.lookup_failed)
        self._task_runner.submit(worker)

    def request_episodes(self, title: str, imdb_id: str, season: int, language_name: str) -> None:
        worker = EpisodeSuggestionWorker(title, imdb_id, season, language_name)
        worker.finished.connect(lambda episodes, season=season: self.episodes_ready.emit(season, episodes))
        worker.failed.connect(self.lookup_failed)
        self._task_runner.submit(worker)
