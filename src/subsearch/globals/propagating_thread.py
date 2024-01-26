from typing import Any
from subsearch.utils import io_log

import threading


class PropagatingThread(threading.Thread):
    def __init__(self, *args, **kwargs) -> None:
        self._target = None
        self._args = ()
        self._kwargs = {}
        super().__init__(*args, **kwargs)
        self.exception = None
        self.return_value = None
        assert self._target

    def run(self) -> None:
        try:
            io_log.log.stdout(f"Thread {self.name} started", level="debug", print_allowed=False)
            if self._target:
                self.return_value = self._target(*self._args, **self._kwargs)
        except Exception as e:
            self.exception = e
        finally:
            del self._target, self._args, self._kwargs

    def join(self, timeout=None) -> Any:
        super().join(timeout)
        if self.exception:
            msg = f"\nError occurred in thread {self.name}\n\tTraceback (most recent call last):\n\t\t{self.exception}"
            io_log.log.stdout(msg, level="error", print_allowed=False)
            raise self.exception
        else:
            io_log.log.stdout(f"Thread {self.name} finnished", level="debug", print_allowed=False)
        return self.return_value


def handle_tasks(*tasks) -> None:
    for thread_count, target in enumerate(tasks, start=1):
        func_name = str(target.__name__).split("_")[-1]
        name = f"thread_{thread_count}_{func_name}"
        task_thread = PropagatingThread(target=target, name=name)
        task_thread.start()
        task_thread.join()
