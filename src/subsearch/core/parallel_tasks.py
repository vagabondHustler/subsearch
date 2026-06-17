import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable

from subsearch.runtime.logging.events import LogEvent
from subsearch.runtime.logging.logger import log


def run_in_threads(*tasks: Callable[..., None]) -> None:
    task_names = [task.__name__.lower() for task in tasks]
    log.event(LogEvent.THREAD_SUBMITTING, level="debug", count=len(tasks), names=", ".join(task_names))
    with ThreadPoolExecutor(thread_name_prefix="provider", max_workers=4) as executor:
        futures = {executor.submit(task): name for task, name in zip(tasks, task_names)}
        for future in as_completed(futures):
            name = futures[future]
            exception = future.exception()
            if exception:
                traceback_text = "".join(traceback.format_exception(exception))
                log.event(LogEvent.THREAD_FAILED, level="error", name=name, traceback=traceback_text)
            else:
                log.event(LogEvent.THREAD_COMPLETED, level="debug", name=name)
    log.event(LogEvent.THREAD_JOINED, level="debug", names=", ".join(task_names))
