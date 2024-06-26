import threading
from typing import Any

from subsearch.globals import log


class CreateThread(threading.Thread):
    def __init__(self, *args, **kwargs) -> None:
        self._target = None
        self._args = ()
        self._kwargs = {}  # type: ignore
        super().__init__(*args, **kwargs)
        self.exception = None
        self.return_value = None
        assert self._target

    def run(self) -> None:
        try:
            log.stdout(f"Thread {self.name} started", level="debug", print_allowed=False)
            if self._target:
                self.return_value = self._target(*self._args, **self._kwargs)
        except Exception as e:
            self.exception = e  # type: ignore
        finally:
            del self._target, self._args, self._kwargs

    def join(self, timeout=None) -> Any:
        super().join(timeout)
        if self.exception:
            msg = f"\nError occurred in thread {self.name}\n\tTraceback (most recent call last):\n\t\t{self.exception}"
            log.stdout(msg, level="error", print_allowed=False)
            raise self.exception
        else:
            log.stdout(f"Thread {self.name} finnished", level="debug", print_allowed=False)
        return self.return_value
