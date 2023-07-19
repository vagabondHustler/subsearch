from dataclasses import dataclass
from enum import Enum
from typing import Any

from subsearch.utils import log


@dataclass(order=True, frozen=True)
class CoreState(Enum):
    UNKNOWN: int = 0
    INITIALIZE: int = 1
    INITIALIZED: int = 2
    OPENSUBTITLES: int = 3
    SUBSCENE: int = 4
    YIFYSUBTITLES: int = 5
    DOWNLOAD_FILES: int = 6
    EXTRACT_FILES: int = 7
    SUMMARY: int = 8
    CLEAN_UP: int = 9
    EXIT: int = 10

    NO_FILE: int = -1
    GUI: int = -2


class CoreStateMachine:
    """
    A class representing a state machine.

    Attributes:
        state (States): The current state of the state machine.

    Methods:
        __init__(): Initializes the StateMachine class.
        _yield_state(): Generator function to yield the next state.
        set_state(state: int): Sets the state of the state machine.
        get_state(): Returns the current state of the state machine.
        _next_state(): Sets the next state of the state machine.
    """

    state = CoreState.UNKNOWN

    def __init__(self) -> None:
        self.locked_states = [CoreState.NO_FILE.name, CoreState.GUI.name, CoreState.EXIT.name]

    def _yeild_state(self):
        current_index = self.state.value
        next_index = current_index + 1
        self.set_state(next_index)
        yield self.state

    def set_state(self, state: int):
        setattr(CoreStateMachine, "state", CoreState(state))
        log.stdout(self.state, print_allowed=False)

    def get_state(self):
        return getattr(CoreStateMachine, "state")

    def _next_state(self):
        if self.state.name not in self.locked_states:
            next(self._yeild_state())

    def update_state(self) -> None:
        self._next_state()

    def lock_to_state(self, state: str) -> None:
        """
        Locks the system tray to a specific state, even if update_progress_state is called

        Args:
            state (str): "no_file", "gui", "exit"
        """
        states = {"no_file": CoreState.NO_FILE.value, "gui": CoreState.GUI.value, "exit": CoreState.EXIT.value}
        self.set_state(states[state])
