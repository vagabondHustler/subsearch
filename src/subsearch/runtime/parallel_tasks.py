from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable

from subsearch.runtime.logger import log


def run_in_threads(*tasks: Callable[..., None]) -> None:
    with ThreadPoolExecutor(thread_name_prefix="provider", max_workers=4) as executor:
        futures = {executor.submit(task): task.__name__.lower() for task in tasks}
        for future in as_completed(futures):
            name = futures[future]
            exception = future.exception()
            if exception:
                msg = f"\nError occurred in thread {name}\n\tTraceback (most recent call last):\n\t\t{exception}"
                log.stdout(msg, level="error", print_allowed=False)
                raise exception
            log.stdout(f"Thread {name} finished", level="debug", print_allowed=False)
