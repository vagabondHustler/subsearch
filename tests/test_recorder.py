import sys
import threading
import time
from pathlib import Path

import pytest

from subsearch.runtime import recorder
from subsearch.runtime.recorder import LogLevel, RecorderConfig
from subsearch.runtime.recorder import standard_in as recorder_door


@pytest.fixture
def fresh_recorder(tmp_path: Path):
    def start(callbacks=()):
        recorder.shutdown()
        recorder.init(
            RecorderConfig(
                log_file_path=tmp_path / "log.log",
                crash_file_path=tmp_path / "crash.log",
                console_outputs=tuple(callbacks),
            )
        )
        return tmp_path

    yield start
    recorder.shutdown()


def _wait_for(predicate, timeout: float = 2.0) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            if predicate():
                return
        except FileNotFoundError, AssertionError:
            pass
        time.sleep(0.02)
    raise AssertionError("condition not met within timeout")


def _phase_titles(snapshot) -> list[str]:
    return [group.title for group in snapshot.groups]


def _active_lines(snapshot) -> list[str]:
    for group in snapshot.groups:
        if group.active:
            return [line.text for line in group.transient_lines]
    return []


def test_capture_writes_log_form_to_log_file(fresh_recorder) -> None:
    tmp_path = fresh_recorder()
    recorder.capture("hello", level=LogLevel.INFO)
    _wait_for(lambda: "hello" in (tmp_path / "log.log").read_text(encoding="utf-8"))


def test_console_callbacks_receive_identical_snapshots(fresh_recorder) -> None:
    stdout_seen: list = []
    ui_seen: list = []
    fresh_recorder(callbacks=(stdout_seen.append, ui_seen.append))
    recorder.capture("Searching", level=LogLevel.PHASE)
    recorder.capture("a warning", level=LogLevel.WARNING)
    _wait_for(
        lambda: stdout_seen
        and "Searching 1 warning" in " ".join(line.text for line in stdout_seen[-1].pinned_summaries)
    )
    # both consoles consume the same snapshot, so the boxes are byte-identical
    assert stdout_seen == ui_seen
    final = stdout_seen[-1]
    assert _phase_titles(final) == ["Searching"]
    summary = final.pinned_summaries[0].text
    assert summary.startswith("Searching 1 warning see ") and summary.endswith(" for details")


def test_debug_is_log_only_but_info_reaches_console_snapshots(fresh_recorder) -> None:
    seen: list = []
    fresh_recorder(callbacks=(seen.append,))
    recorder.capture("internal detail", level=LogLevel.DEBUG)
    recorder.capture("status", level=LogLevel.INFO)
    # debug never opens a group or rolls a transient line; info rolls into the active group
    _wait_for(lambda: seen and _active_lines(seen[-1]) == ["status"])


def test_capture_preserves_order(fresh_recorder) -> None:
    seen: list = []
    fresh_recorder(callbacks=(seen.append,))
    for index in range(20):
        recorder.capture(f"banner {index}", level=LogLevel.PHASE)
    _wait_for(lambda: seen and _phase_titles(seen[-1]) == [f"banner {index}" for index in range(20)])


def test_capture_before_init_is_replayed(tmp_path: Path) -> None:
    recorder.shutdown()
    seen: list = []
    recorder.capture("early banner", level=LogLevel.PHASE)
    recorder.init(
        RecorderConfig(
            log_file_path=tmp_path / "log.log",
            crash_file_path=tmp_path / "crash.log",
            console_outputs=(seen.append,),
        )
    )
    _wait_for(lambda: seen and _phase_titles(seen[-1]) == ["early banner"])
    recorder.shutdown()


def test_flush_crash_writes_crash_file(fresh_recorder) -> None:
    tmp_path = fresh_recorder()
    recorder.flush_crash("worker-1", "Traceback ...\nValueError: boom")
    crash = (tmp_path / "crash.log").read_text(encoding="utf-8")
    assert "worker-1" in crash
    assert "ValueError: boom" in crash


def test_capture_never_raises_after_shutdown() -> None:
    recorder.shutdown()
    recorder.capture("after shutdown", level=LogLevel.INFO)


def test_shutdown_emits_exiting_phase_with_elapsed_run_time(tmp_path: Path) -> None:
    recorder.shutdown()
    seen: list[str] = []
    recorder.init(
        RecorderConfig(
            log_file_path=tmp_path / "log.log",
            crash_file_path=tmp_path / "crash.log",
            console_outputs=(seen.append,),
            start_perf_counter=time.perf_counter(),
        )
    )
    recorder.shutdown()
    titles = [title for snapshot in seen for title in _phase_titles(snapshot)]
    assert any(title.startswith("Exiting after ") and title.endswith(" seconds") for title in titles)


def test_shutdown_reports_run_finished_without_start_counter(tmp_path: Path) -> None:
    recorder.shutdown()
    seen: list[str] = []
    recorder.init(
        RecorderConfig(
            log_file_path=tmp_path / "log.log",
            crash_file_path=tmp_path / "crash.log",
            console_outputs=(seen.append,),
        )
    )
    recorder.shutdown()
    titles = [title for snapshot in seen for title in _phase_titles(snapshot)]
    assert "Exiting " in titles


def test_concurrent_capture_from_two_threads_loses_nothing(fresh_recorder) -> None:
    seen: list = []
    fresh_recorder(callbacks=(seen.append,))
    captures_per_thread = 200

    def hammer(prefix: str) -> None:
        for index in range(captures_per_thread):
            recorder.capture(f"{prefix}-{index}", level=LogLevel.PHASE)

    first = threading.Thread(target=hammer, args=("a",))
    second = threading.Thread(target=hammer, args=("b",))
    first.start()
    second.start()
    first.join()
    second.join()

    expected = sorted(
        [f"a-{index}" for index in range(captures_per_thread)] + [f"b-{index}" for index in range(captures_per_thread)]
    )
    # each unique banner opens its own group; the final snapshot accumulates all of them
    _wait_for(lambda: seen and sorted(_phase_titles(seen[-1])) == expected)


def test_worker_thread_crash_reaches_crash_file(tmp_path: Path) -> None:
    recorder.shutdown()
    saved_threadhook = threading.excepthook
    threading.excepthook = lambda args: None  # the recorder chains onto this no-op, not pytest's catcher
    try:
        recorder.init(
            RecorderConfig(
                log_file_path=tmp_path / "log.log",
                crash_file_path=tmp_path / "crash.log",
            )
        )

        def crashing_worker() -> None:
            raise ValueError("worker exploded")

        worker = threading.Thread(target=crashing_worker, name="doomed-worker")
        worker.start()
        worker.join()

        _wait_for(lambda: "doomed-worker" in (tmp_path / "crash.log").read_text(encoding="utf-8"))
        crash = (tmp_path / "crash.log").read_text(encoding="utf-8")
        assert "ValueError: worker exploded" in crash
    finally:
        recorder.shutdown()
        threading.excepthook = saved_threadhook


def test_every_crash_surface_reaches_crash_file(tmp_path: Path) -> None:
    recorder.shutdown()
    saved_excepthook = sys.excepthook
    saved_threadhook = threading.excepthook
    saved_unraisablehook = sys.unraisablehook
    # Chain the recorder's hooks onto silent no-ops so the test owns every crash surface
    # and pytest's own catchers never see the re-raised exceptions.
    sys.excepthook = lambda *args: None
    threading.excepthook = lambda args: None
    sys.unraisablehook = lambda args: None
    try:
        recorder.init(
            RecorderConfig(
                log_file_path=tmp_path / "log.log",
                crash_file_path=tmp_path / "crash.log",
            )
        )

        def crash_text() -> str:
            path = tmp_path / "crash.log"
            return path.read_text(encoding="utf-8") if path.exists() else ""

        try:
            raise RuntimeError("main thread boom")
        except RuntimeError as error:
            sys.excepthook(type(error), error, error.__traceback__)
        _wait_for(lambda: "main thread boom" in crash_text())

        def worker_boom() -> None:
            raise KeyError("worker hook boom")

        worker = threading.Thread(target=worker_boom, name="hooked-worker")
        worker.start()
        worker.join()
        _wait_for(lambda: "worker hook boom" in crash_text() and "hooked-worker" in crash_text())

        try:
            raise SystemError("unraisable boom")
        except SystemError as error:
            unraisable_args = type(
                "UnraisableArgs",
                (),
                {
                    "exc_type": type(error),
                    "exc_value": error,
                    "exc_traceback": error.__traceback__,
                    "err_msg": None,
                    "object": None,
                },
            )()
            sys.unraisablehook(unraisable_args)
        _wait_for(lambda: "unraisable boom" in crash_text())
    finally:
        recorder.shutdown()
        sys.excepthook = saved_excepthook
        threading.excepthook = saved_threadhook
        sys.unraisablehook = saved_unraisablehook


def test_drain_thread_fatal_error_flushes_its_own_crash(fresh_recorder) -> None:
    tmp_path = fresh_recorder()
    live_recorder = recorder_door._recorder
    assert live_recorder is not None

    def explode_drain_loop() -> None:
        raise RuntimeError("router queue corrupted")

    live_recorder._drain_loop = explode_drain_loop  # type: ignore[method-assign]
    live_recorder._drain()  # the fatal-guard wrapper must turn a drain-loop crash into a flushed crash session

    crash = (tmp_path / "crash.log").read_text(encoding="utf-8")
    assert "flight-recorder" in crash
    assert "router queue corrupted" in crash
