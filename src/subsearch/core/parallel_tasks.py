import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable

from subsearch.runtime.logging.logger import log


def run_in_threads(*tasks: Callable[..., None]) -> None:
    task_names = [task.__name__.lower() for task in tasks]
    log.debug(f"Submitting {len(tasks)} thread(s): {', '.join(task_names)}")
    with ThreadPoolExecutor(thread_name_prefix="provider", max_workers=4) as executor:
        futures = {executor.submit(task): name for task, name in zip(tasks, task_names)}
        for future in as_completed(futures):
            name = futures[future]
            exception = future.exception()
            if exception:
                traceback_text = "".join(traceback.format_exception(exception))
                log.error(f"Thread {name} raised an exception\n{traceback_text}", to_console=False)
            else:
                log.debug(f"Thread {name} completed")
    log.debug(f"All threads joined: {', '.join(task_names)}")
