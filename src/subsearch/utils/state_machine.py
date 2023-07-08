from dataclasses import dataclass
from enum import Enum, auto


class _Subsearch(Enum):
    UNKNOWN = auto()
    INITIALIZING = auto()
    INITIALIZED = auto()
    INITIALIZING_SEARCH = auto()
    SUBSCENE_STARTED = auto()
    OPENSUBS_STARTED = auto()
    YIFYSUBS_STARTED = auto()
    SUBSCENE_ENDED = auto()
    OPENSUBS_ENDED = auto()
    YIFYSUBS_ENDED = auto()
    DOWNLOADING_FILES = auto()
    EXTRACTING_FILES = auto()
    CLEANING_UP = auto()
    EXITING = auto()
    NO_FILE_FOUND = auto()


class StateHelper:
    previous_states: list[Enum] = []

    @classmethod
    def __create__(cls, state: Enum) -> None:
        cls.__state = state

    def set_state(self, state: Enum) -> None:
        self.__state = state
        self.previous_states.append(state)

    @property
    def state(self) -> Enum:
        return self.__state

    @property
    def search_ran(self) -> bool:
        providers_ended = [_Subsearch.SUBSCENE_ENDED, _Subsearch.OPENSUBS_ENDED, _Subsearch.YIFYSUBS_ENDED]
        if _Subsearch.INITIALIZING not in self.previous_states:
            return False
        elif any(provider in self.previous_states for provider in providers_ended):
            return _Subsearch.SEARCHING in self.previous_states
        return False

    @property
    def file_exist(self) -> bool:
        return _Subsearch.NO_FILE_FOUND not in self.previous_states


@dataclass(frozen=True, order=True)
class Subsearch(StateHelper):
    UNKNOWN: _Subsearch = _Subsearch.UNKNOWN
    INITIALIZING: _Subsearch = _Subsearch.INITIALIZING
    INITIALIZED: _Subsearch = _Subsearch.INITIALIZED
    INITIALIZING_SEARCH: _Subsearch = _Subsearch.INITIALIZING_SEARCH
    SUBSCENE_STARTED: _Subsearch = _Subsearch.SUBSCENE_STARTED
    OPENSUBS_STARTED: _Subsearch = _Subsearch.OPENSUBS_STARTED
    YIFYSUBS_STARTED: _Subsearch = _Subsearch.YIFYSUBS_STARTED
    SUBSCENE_ENDED: _Subsearch = _Subsearch.SUBSCENE_ENDED
    OPENSUBS_ENDED: _Subsearch = _Subsearch.OPENSUBS_ENDED
    YIFYSUBS_ENDED: _Subsearch = _Subsearch.YIFYSUBS_ENDED
    DOWNLOADING_FILES: _Subsearch = _Subsearch.DOWNLOADING_FILES
    EXTRACTING_FILES: _Subsearch = _Subsearch.EXTRACTING_FILES
    CLEANING_UP: _Subsearch = _Subsearch.CLEANING_UP
    EXITING: _Subsearch = _Subsearch.EXITING
    NO_FILE_FOUND: _Subsearch = _Subsearch.NO_FILE_FOUND
