import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable

from subsearch.io.toml_file import diagnostics_enabled
from subsearch.runtime.logging.logger import log


def run_in_threads(*tasks: Callable[..., None]) -> None:
    task_names = [task.__name__.lower() for task in tasks]
    if diagnostics_enabled():
        log.debug(f"Submitting {len(tasks)} thread(s): {', '.join(task_names)}", to_console=False)
    with ThreadPoolExecutor(thread_name_prefix="provider", max_workers=4) as executor:
        futures = {executor.submit(task): name for task, name in zip(tasks, task_names)}
        for future in as_completed(futures):
            name = futures[future]
            exception = future.exception()
            if exception:
                traceback_text = "".join(traceback.format_exception(exception))
                log.error(f"\nError occurred in thread {name}\n{traceback_text}", to_console=False)
                continue
            if diagnostics_enabled():
                log.debug(f"Thread {name} finished", to_console=False)
