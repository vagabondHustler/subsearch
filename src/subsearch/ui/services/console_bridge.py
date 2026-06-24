from typing import Callable

from subsearch.runtime.recorder import ConsoleSnapshot


class ConsoleBridge:
    def __init__(self) -> None:
        self._listener: Callable[[ConsoleSnapshot], None] | None = None

    def attach(self, listener: Callable[[ConsoleSnapshot], None]) -> None:
        self._listener = listener

    def detach(self) -> None:
        self._listener = None

    def emit(self, snapshot: ConsoleSnapshot) -> None:
        if self._listener is not None:
            self._listener(snapshot)


CONSOLE_BRIDGE = ConsoleBridge()
