import atexit
import sys
import threading
import time
import traceback
from collections import deque
from typing import TYPE_CHECKING

from subsearch.runtime.recorder._black_box.recorded_entry import RecordedEntry
from subsearch.runtime.recorder._black_box.run_data_recorder import RunDataRecorder
from subsearch.runtime.recorder.config import LogLevel, RecorderConfig

if TYPE_CHECKING:
    from subsearch.runtime.recorder._black_box.file_tracker import FileTracker

_PRE_INIT_BUFFER_SIZE = 1000

_recorder: RunDataRecorder | None = None
_start_perf_counter: float | None = None
_file_tracker: "FileTracker | None" = None
_pre_init_buffer: deque[RecordedEntry] = deque(maxlen=_PRE_INIT_BUFFER_SIZE)
_lock = threading.Lock()


def init(config: RecorderConfig) -> None:
    """Start the recorder drain thread, flush the pre-init buffer, and install crash hooks.

    Idempotent — a second call while already running is a no-op.
    """
    global _recorder, _start_perf_counter
    with _lock:
        if _recorder is not None:
            return
        recorder = RunDataRecorder(config)
        recorder.start()
        _recorder = recorder
        _start_perf_counter = config.start_perf_counter
        _install_crash_hooks()
        atexit.register(shutdown)
        capture(_startup_summary(), level=LogLevel.DEBUG)
        while _pre_init_buffer:
            recorder.enqueue(_pre_init_buffer.popleft())


def capture(*lines: str, level: LogLevel = LogLevel.INFO) -> None:
    """Submit one or more log lines to the recorder.

    Safe to call before ``init()`` (buffered) and after ``shutdown()`` (silenced).
    Never raises.
    """
    try:
        module, line_number = _caller_location()
        entry = RecordedEntry(
            lines=tuple(lines),
            level=level,
            module=module,
            line_number=line_number,
            captured_at=time.time(),
        )
        if _recorder is None:
            _pre_init_buffer.append(entry)
        else:
            _recorder.enqueue(entry)
    except Exception:
        return


def phase(*lines: str) -> None:
    """Submit one or more phase banners — the headline steps shown on the console and spinner.

    Thin wrapper over ``capture`` that owns the phase level so callers never name it.
    """
    capture(*lines, level=LogLevel.PHASE)


def flush_crash(thread_name: str, traceback_text: str) -> None:
    """Write a crash traceback synchronously, bypassing the queue.

    Called from the three crash hooks installed by ``init()``; safe to call from any
    thread at any time the recorder is running.
    """
    if _recorder is not None:
        _recorder.flush_crash(thread_name, traceback_text)


def shutdown() -> None:
    """Drain the queue, join the drain thread, and close all outputs.

    Idempotent — safe to call more than once. Registered with ``atexit`` by ``init()``.
    """
    global _recorder, _start_perf_counter
    with _lock:
        if _recorder is None:
            return

        phase(f"Exiting {_elapsed_time()}")
        capture("recorder shutting down, draining queue", level=LogLevel.DEBUG)
        _recorder.shutdown()
        _recorder = None
        _start_perf_counter = None


def _startup_summary() -> str:
    count = len(_pre_init_buffer)
    if count == 0:
        return "recorder started, no pre-init entries buffered"
    window_seconds = _pre_init_buffer[-1].captured_at - _pre_init_buffer[0].captured_at
    modules = ", ".join(dict.fromkeys(entry.module for entry in _pre_init_buffer))
    summary = f"recorder started, flushing {count} pre-init entries over {window_seconds:.3f}s from {modules}"
    if count == _PRE_INIT_BUFFER_SIZE:
        summary += " (buffer full, oldest entries may have been dropped)"
    return summary


def _elapsed_time() -> str:
    if _start_perf_counter is None:
        return ""
    return f"after {time.perf_counter() - _start_perf_counter:.2f} seconds"


def _caller_location() -> tuple[str, int]:
    frame = sys._getframe(2)
    module = frame.f_globals.get("__name__", "?").rsplit(".", 1)[-1]
    return module, frame.f_lineno


def get_file_tracker() -> "FileTracker":
    """Return the module-level FileTracker singleton, creating it on first call."""
    global _file_tracker
    if _file_tracker is None:
        from subsearch.runtime.config import APP_PATHS
        from subsearch.runtime.recorder._black_box.file_tracker import FileTracker

        _file_tracker = FileTracker(APP_PATHS.appdata_subsearch / "tracked_files.json")
    return _file_tracker


def _install_crash_hooks() -> None:
    previous_excepthook = sys.excepthook
    previous_threadhook = threading.excepthook
    previous_unraisablehook = sys.unraisablehook

    def on_uncaught(exc_type, exc_value, exc_traceback):  # type: ignore[no-untyped-def]
        traceback_text = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        flush_crash(threading.current_thread().name, traceback_text)
        previous_excepthook(exc_type, exc_value, exc_traceback)

    def on_thread_crash(args: threading.ExceptHookArgs) -> None:
        traceback_text = "".join(traceback.format_exception(args.exc_type, args.exc_value, args.exc_traceback))
        thread_name = args.thread.name if args.thread is not None else "thread"
        flush_crash(thread_name, traceback_text)
        previous_threadhook(args)

    def on_unraisable(args) -> None:  # type: ignore[no-untyped-def]
        traceback_text = "".join(traceback.format_exception(args.exc_type, args.exc_value, args.exc_traceback))
        flush_crash("unraisable", traceback_text)
        previous_unraisablehook(args)

    sys.excepthook = on_uncaught
    threading.excepthook = on_thread_crash
    sys.unraisablehook = on_unraisable
