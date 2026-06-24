import queue
import threading
import traceback
from datetime import datetime

from subsearch.runtime.recorder.config import RecorderConfig
from subsearch.runtime.recorder._black_box.formatting import EntryFormatter
from subsearch.runtime.recorder._black_box.standard_out.console_output import ConsoleOutput
from subsearch.runtime.recorder._black_box.standard_error.crash_file_output import CrashFileOutput
from subsearch.runtime.recorder._black_box.standard_out.log_file_output import RotatingLogFileOutput
from subsearch.runtime.recorder._black_box.recorded_entry import RecordedEntry
from subsearch.runtime.recorder._black_box.routing import EntryRouter

_QUEUE_MAX_SIZE = 10_000


class _Sentinel:
    pass


_SENTINEL = _Sentinel()


class RunDataRecorder:
    def __init__(self, config: RecorderConfig) -> None:
        self._tick_seconds = config.tick_seconds
        self._queue: queue.Queue[RecordedEntry | _Sentinel] = queue.Queue(maxsize=_QUEUE_MAX_SIZE)
        self._router = EntryRouter(
            EntryFormatter(),
            ConsoleOutput(config.console_outputs, config.transient_window_size, config.log_file_path.name),
            RotatingLogFileOutput(config.log_file_path, config.log_max_bytes),
            CrashFileOutput(config.crash_file_path, config.log_max_bytes, config.crash_clear_every_runs),
        )
        self._thread = threading.Thread(target=self._drain, name="flight-recorder", daemon=True)

    def start(self) -> None:
        self._thread.start()

    def enqueue(self, entry: RecordedEntry) -> None:
        try:
            self._queue.put_nowait(entry)
        except queue.Full:
            return

    def flush_crash(self, thread_name: str, traceback_text: str) -> None:
        try:
            header = f"{thread_name} {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            self._router.route_crash(f"{header}\n{traceback_text}")
        except Exception:
            return

    def shutdown(self) -> None:
        try:
            self._queue.put_nowait(_SENTINEL)
        except queue.Full:
            pass
        self._thread.join(timeout=2.0)
        self._router.close()

    def _drain(self) -> None:
        try:
            self._drain_loop()
        except Exception:
            self.flush_crash("flight-recorder", traceback.format_exc())

    def _drain_loop(self) -> None:
        while True:
            try:
                entry = self._queue.get(timeout=self._tick_seconds)
            except queue.Empty:
                self._safe_tick()
                continue
            if isinstance(entry, _Sentinel):
                break
            self._safe_route(entry)
            self._queue.task_done()

    def _safe_route(self, entry: RecordedEntry) -> None:
        try:
            self._router.route(entry)
        except Exception:
            return

    def _safe_tick(self) -> None:
        try:
            self._router.tick()
        except Exception:
            return
