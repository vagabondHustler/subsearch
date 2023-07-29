from dataclasses import dataclass
from enum import Enum, auto
from typing import Generator, Union

from subsearch.utils import io_log


@dataclass(order=True, frozen=True)
class DataState(Enum):
    UNKNOWN = auto()
    INITIALIZING_APP_PATHS = auto()
    INITIALIZING_FILE_DATA = auto()
    INITIALIZING_DEVICE_INFO = auto()


@dataclass(order=True, frozen=True)
class CoreState(Enum):
    UNKNOWN = auto()
    INITIALIZE = auto()
    INITIALIZED = auto()
    CALL_OPENSUBTITLES = auto()
    CALL_SUBSCENE = auto()
    CALL_YIFYSUBTITLES = auto()
    DOWNLOAD_FILES = auto()
    MANUAL_DOWNLOAD = auto()
    AUTOLOAD_RENAME = auto()
    AUTOLOAD_MOVE = auto()
    AUTOLOAD_MOVE_ALL = auto()
    EXTRACT_FILES = auto()
    SUMMARY_TOAST = auto()
    CLEAN_UP = auto()
    EXIT = auto()

    NO_FILE = auto()
    GUI = auto()


@dataclass(order=True, frozen=True)
class SubsceneState(Enum):
    UNKNOWN = auto()
    WORKING = auto()
    FINNISHED = auto()


@dataclass(order=True, frozen=True)
class OpenSubtitlesState(Enum):
    UNKNOWN = auto()
    WORKING = auto()
    FINNISHED = auto()


@dataclass(order=True, frozen=True)
class YifySubtitlesState(Enum):
    UNKNOWN = auto()
    WORKING = auto()
    FINNISHED = auto()


class Singleton(type):
    _instances: dict[type, type] = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class StateManager(metaclass=Singleton):
    current_state: Enum
    enum_class = type[Union[DataState, CoreState, SubsceneState, OpenSubtitlesState, YifySubtitlesState]]
    state_history: list[Enum] = []

    def __init__(self, _enum_class: enum_class) -> None:
        self.current_state = self.set_state(_enum_class.UNKNOWN)

    def _yield_state(self) -> Generator:
        current_state = self.current_state
        state_names = [state for state in self.current_state.__class__]
        current_index = state_names.index(current_state)

        next_index = current_index + 1
        if next_index >= len(state_names):
            next_index = 0

        self.set_state(state_names[next_index])
        yield self.current_state

    def set_state(self, state: Enum):
        self.current_state = state
        self.state_history.append(self.current_state)
        io_log.stdout(self.current_state, level="debug", print_allowed=False)

    def get_state(self) -> Enum:
        return self.current_state

    def get_state_history(self) -> list[Enum]:
        return self.state_history

    def update_state(self) -> None:
        next(self._yield_state())


class DataStateManager(StateManager):
    def __init__(self) -> None:
        self.state = DataState
        super().__init__(self.state)


class CoreStateManager(StateManager):
    def __init__(self) -> None:
        self.state = CoreState
        super().__init__(self.state)


class SubsceneStateManager(StateManager):
    def __init__(self) -> None:
        self.state = SubsceneState
        super().__init__(self.state)


class OpenSubtitlesStateManager(StateManager):
    def __init__(self) -> None:
        self.state = OpenSubtitlesState
        super().__init__(self.state)


class YifySubtitlesStateManager(StateManager):
    def __init__(self) -> None:
        self.state = YifySubtitlesState
        super().__init__(self.state)


def initialize_manager(instance):
    manager = instance()
    manager.set_state(manager.state.WORKING)
