import threading
import time

import pytest

from subsearch.runtime import parallel_tasks


def test_runs_every_task() -> None:
    completed = []
    lock = threading.Lock()

    def make_task(label):
        def task():
            with lock:
                completed.append(label)

        task.__name__ = f"task_{label}"
        return task

    parallel_tasks.run_in_threads(make_task("a"), make_task("b"), make_task("c"))

    assert sorted(completed) == ["a", "b", "c"]


def test_tasks_run_concurrently_not_serially() -> None:
    barrier = threading.Barrier(3)

    def task():
        barrier.wait(timeout=2)

    start = time.perf_counter()
    parallel_tasks.run_in_threads(task, task, task)
    elapsed = time.perf_counter() - start

    assert elapsed < 2


def test_worker_exception_propagates() -> None:
    def fine() -> None:
        pass

    def boom() -> None:
        raise ValueError("kaboom")

    with pytest.raises(ValueError, match="kaboom"):
        parallel_tasks.run_in_threads(fine, boom)
