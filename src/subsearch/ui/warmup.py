import importlib
import threading

_warmup_thread: threading.Thread | None = None


def start_warmup() -> None:
    global _warmup_thread
    if _warmup_thread is not None:
        return
    _warmup_thread = threading.Thread(
        target=importlib.import_module,
        args=("subsearch.ui.application",),
        daemon=True,
    )
    _warmup_thread.start()


def await_warmup() -> None:
    if _warmup_thread is not None:
        _warmup_thread.join()
