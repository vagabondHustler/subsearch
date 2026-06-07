import threading
import time

from subsearch.runtime.config import parallel_tasks


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


def test_worker_exception_is_logged_without_aborting_siblings() -> None:
    completed = []

    def fine() -> None:
        completed.append("fine")

    def boom() -> None:
        raise ValueError("kaboom")

    parallel_tasks.run_in_threads(fine, boom)

    assert completed == ["fine"]
