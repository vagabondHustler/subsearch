from dataclasses import dataclass
from enum import Enum


@dataclass(order=True, frozen=True)
class States(Enum):
    UNKNOWN: Enum = 0
    INITIALIZE: Enum = 1
    INITIALIZED: Enum = 2
    OPENSUBTITLES: Enum = 3
    SUBSCENE: Enum = 4
    YIFYSUBTITLES: Enum = 5
    DOWNLOAD_FILES: Enum = 6
    EXTRACT_FILES: Enum = 7
    SUMMARY: Enum = 8
    CLEAN_UP: Enum = 9
    EXIT: Enum = 10

    NO_FILE: Enum = -1
    GUI: Enum = -2


class StateMachine:
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

    state = States.UNKNOWN

    def __init__(self) -> None:
        self.locked_states = [States.NO_FILE.name, States.GUI.name, States.EXIT.name]

    def _yeild_state(self):
        current_index = self.state.value
        next_index = current_index + 1
        self.set_state(next_index)
        yield self.state

    def set_state(self, state: int):
        setattr(StateMachine, "state", States(state))

    def get_state(self):
        return getattr(StateMachine, "state")

    def _next_state(self):
        if self.state.name not in self.locked_states:
            next(self._yeild_state())
