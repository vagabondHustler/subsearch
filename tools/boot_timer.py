"""Profile Subsearch booting into settings mode, until the window is shown.

Drives the real settings-mode path with no path argument (process start -> Bootstrap ->
open_settings_window -> window.show()) and stops the moment the window becomes visible.
The window is closed immediately so the profiler can finish.

    .venv/Scripts/python.exe -m tools.boot_timer                 # pyinstrument call tree
    .venv/Scripts/python.exe -m tools.boot_timer --view tree     # same, explicit
    .venv/Scripts/python.exe -m tools.boot_timer --open          # + open HTML flamegraph
    .venv/Scripts/python.exe -m tools.boot_timer --view timeline # viztracer Perfetto timeline
    .venv/Scripts/python.exe -m tools.boot_timer --view timeline --open
    .venv/Scripts/python.exe -m tools.boot_timer --cold          # cold-FS boots (self-elevates via UAC)
    .venv/Scripts/python.exe -m tools.boot_timer --cold --runs 7 # custom iteration count

Measure one boot per process: import caches and singletons make any second boot
in the same process unrepresentative.

The --cold mode evicts cached .pyc files from RAM before each boot so disk reads
are genuinely cold. Flushing the Windows standby list needs admin rights, so the
tool relaunches itself through UAC; accept the prompt to continue.
"""

import argparse
import ctypes
import subprocess
import sys
import time
import webbrowser
from pathlib import Path

_REPORTS_DIRECTORY = Path(__file__).resolve().parent / "_boot_profiles"
_ELAPSED_PREFIX = "BOOT_ELAPSED_MS="


def _drive_boot_until_window_shown() -> float:
    """Run a full settings-mode boot, close the window once shown, return seconds elapsed."""
    sys.argv = ["subsearch"]

    from PySide6.QtCore import QTimer

    from subsearch.core.pipeline import SearchPipeline
    from subsearch.ui import entrypoint
    from subsearch.ui.core.window import SettingsWindow

    shown_at: list[float] = []
    original_open = entrypoint.open_settings_window

    def close_active_window() -> None:
        for widget in entrypoint.get_application().topLevelWidgets():
            if isinstance(widget, SettingsWindow):
                widget.close()

    def open_and_close_when_shown(*arguments, **keyword_arguments):  # type: ignore[no-untyped-def]
        caller_callback = keyword_arguments.get("on_window_shown", lambda: None)

        def on_shown() -> None:
            shown_at.append(time.perf_counter())
            caller_callback()
            QTimer.singleShot(0, close_active_window)

        keyword_arguments["on_window_shown"] = on_shown
        return original_open(*arguments, **keyword_arguments)

    entrypoint.open_settings_window = open_and_close_when_shown

    started = time.perf_counter()
    pipeline = SearchPipeline(started)
    if pipeline.bootstrap.app_mode.name != "SETTINGS":
        raise SystemExit(f"Expected SETTINGS mode, booted into {pipeline.bootstrap.app_mode.name}")

    pipeline.run()

    if not shown_at:
        raise SystemExit("Window never reported shown")
    return shown_at[0] - started


def _is_admin() -> bool:
    return bool(ctypes.windll.shell32.IsUserAnAdmin())


def _spawn_elevated_worker(runs: int) -> None:
    """Launch a visible elevated worker via UAC; it streams progress to the log file."""
    worker_arguments = subprocess.list2cmdline(["-m", "tools.boot_timer", "--cold-worker", "--runs", str(runs)])
    show_normal = 1  # SW_SHOWNORMAL: a visible console so UAC and worker output appear in the integrated terminal
    result = ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, worker_arguments, None, show_normal)
    accepted_threshold = 32  # ShellExecuteW returns <=32 on failure (including UAC denial)
    if result <= accepted_threshold:
        raise SystemExit("Elevation was declined; cold-FS measurement needs admin rights.")


def _enable_privilege(privilege_name: str) -> None:
    """Enable a privilege on the current process token (admin tokens hold it but leave it disabled)."""

    class _LUID(ctypes.Structure):
        _fields_ = [("low_part", ctypes.c_uint32), ("high_part", ctypes.c_int32)]

    class _LUID_AND_ATTRIBUTES(ctypes.Structure):
        _fields_ = [("luid", _LUID), ("attributes", ctypes.c_uint32)]

    class _TOKEN_PRIVILEGES(ctypes.Structure):
        _fields_ = [("count", ctypes.c_uint32), ("privilege", _LUID_AND_ATTRIBUTES)]

    advapi = ctypes.windll.advapi32
    kernel = ctypes.windll.kernel32
    # Declare handle-returning/handle-taking prototypes so 64-bit handles aren't truncated to int.
    kernel.GetCurrentProcess.restype = ctypes.c_void_p
    advapi.OpenProcessToken.argtypes = [ctypes.c_void_p, ctypes.c_uint32, ctypes.POINTER(ctypes.c_void_p)]

    token = ctypes.c_void_p()
    token_adjust_privileges = 0x0020
    token_query = 0x0008
    if not advapi.OpenProcessToken(
        kernel.GetCurrentProcess(), token_adjust_privileges | token_query, ctypes.byref(token)
    ):
        raise SystemExit(f"OpenProcessToken failed (error {ctypes.GetLastError()}).")

    luid = _LUID()
    if not advapi.LookupPrivilegeValueW(None, privilege_name, ctypes.byref(luid)):
        raise SystemExit(f"LookupPrivilegeValueW failed (error {ctypes.GetLastError()}).")

    privilege_enabled = 0x00000002
    privileges = _TOKEN_PRIVILEGES(count=1, privilege=_LUID_AND_ATTRIBUTES(luid=luid, attributes=privilege_enabled))
    advapi.AdjustTokenPrivileges.argtypes = [
        ctypes.c_void_p,
        ctypes.c_bool,
        ctypes.POINTER(_TOKEN_PRIVILEGES),
        ctypes.c_uint32,
        ctypes.c_void_p,
        ctypes.c_void_p,
    ]
    if not advapi.AdjustTokenPrivileges(token, False, ctypes.byref(privileges), 0, None, None):
        raise SystemExit(f"AdjustTokenPrivileges failed (error {ctypes.GetLastError()}).")
    if ctypes.GetLastError() != 0:  # AdjustTokenPrivileges returns success but sets ERROR_NOT_ALL_ASSIGNED
        raise SystemExit(f"Privilege {privilege_name} not held by this token.")


def _flush_file_cache() -> None:
    """Evict cached file pages from RAM so the next .pyc reads hit disk cold."""
    _enable_privilege("SeIncreaseQuotaPrivilege")
    file_cache_min = ctypes.c_size_t(-1)
    file_cache_max = ctypes.c_size_t(-1)
    flags = 0
    if not ctypes.windll.kernel32.SetSystemFileCacheSize(file_cache_min, file_cache_max, flags):
        raise SystemExit(f"SetSystemFileCacheSize failed (error {ctypes.GetLastError()}).")


def _run_single_boot_subprocess() -> float:
    """Spawn a fresh interpreter that boots once and prints its elapsed milliseconds."""
    completed = subprocess.run(
        [sys.executable, "-m", "tools.boot_timer", "--single"],
        capture_output=True,
        text=True,
        check=True,
    )
    for line in completed.stdout.splitlines():
        if line.startswith(_ELAPSED_PREFIX):
            return float(line[len(_ELAPSED_PREFIX) :])
    raise SystemExit(f"Worker did not report elapsed time:\n{completed.stdout}\n{completed.stderr}")


_COLD_LOG_PATH = _REPORTS_DIRECTORY / "cold_boot_progress.log"
_COLD_DONE_MARKER = "COLD_RUN_DONE"


def _run_cold_worker(runs: int) -> None:
    """Elevated, visible console: flush the cache and boot `runs` times, streaming each line to the log."""
    _REPORTS_DIRECTORY.mkdir(exist_ok=True)
    samples: list[float] = []
    with _COLD_LOG_PATH.open("w", encoding="utf-8", buffering=1) as log:

        def emit(line: str) -> None:
            log.write(f"{line}\n")
            print(line)

        try:
            for iteration in range(1, runs + 1):
                _flush_file_cache()
                elapsed_milliseconds = _run_single_boot_subprocess()
                samples.append(elapsed_milliseconds)
                emit(f"  cold boot {iteration}/{runs}: {elapsed_milliseconds:7.1f} ms")

            ordered = sorted(samples)
            median = ordered[len(ordered) // 2]
            emit(f"\nCold-FS boot into settings mode ({runs} runs):")
            emit(f"  min {ordered[0]:.1f} ms   median {median:.1f} ms   max {ordered[-1]:.1f} ms")
        except BaseException as error:  # always release the coordinator, even on flush/boot failure
            emit(f"\nCold run failed: {error!r}")
            raise
        finally:
            # Marker must be written last so the coordinator stops tailing only after all output is flushed.
            log.write(f"{_COLD_DONE_MARKER}\n")

    input("\nPress Enter to close this elevated window...")


def _measure_cold_boots(runs: int) -> None:
    """Coordinator (runs in your terminal): spawn the elevated worker and tail its log live."""
    # Reset the log so we only tail this run's output.
    _REPORTS_DIRECTORY.mkdir(exist_ok=True)
    _COLD_LOG_PATH.write_text("", encoding="utf-8")

    print("Requesting admin rights (UAC) to flush the file cache for cold-FS boots...")
    _spawn_elevated_worker(runs)
    print(f"Elevated worker running headless; tailing {_COLD_LOG_PATH}\n")

    printed_lines = 0
    started_waiting = time.perf_counter()
    seconds_per_boot_budget = 30  # generous: cold disk boots plus interpreter startup per run
    deadline = started_waiting + 20 + runs * seconds_per_boot_budget
    while True:
        lines = _COLD_LOG_PATH.read_text(encoding="utf-8").splitlines()
        for line in lines[printed_lines:]:
            if line != _COLD_DONE_MARKER:
                print(line)
        printed_lines = len(lines)
        if _COLD_DONE_MARKER in lines:
            break
        if time.perf_counter() > deadline:
            print("\nTimed out waiting for the elevated worker (UAC denied, or the worker stalled).")
            return
        time.sleep(0.25)
    print(f"\nDone. Full log: {_COLD_LOG_PATH}")


def _profile_with_pyinstrument(open_report: bool) -> None:
    from pyinstrument import Profiler

    profiler = Profiler()
    profiler.start()
    elapsed = _drive_boot_until_window_shown()
    profiler.stop()

    print(f"\nBoot into settings mode until window shown: {elapsed * 1000:.1f} ms\n")
    profiler.print(show_all=False)

    if open_report:
        _REPORTS_DIRECTORY.mkdir(exist_ok=True)
        report_path = _REPORTS_DIRECTORY / "boot_profile.html"
        report_path.write_text(profiler.output_html(), encoding="utf-8")
        print(f"Flamegraph: {report_path}")
        webbrowser.open(report_path.as_uri())


def _profile_with_viztracer(open_report: bool) -> None:
    from viztracer import VizTracer

    _REPORTS_DIRECTORY.mkdir(exist_ok=True)
    report_path = _REPORTS_DIRECTORY / "boot_timeline.json"

    tracer = VizTracer(output_file=str(report_path))
    tracer.start()
    elapsed = _drive_boot_until_window_shown()
    tracer.stop()
    tracer.save()

    print(f"\nBoot into settings mode until window shown: {elapsed * 1000:.1f} ms")
    print(f"Timeline trace: {report_path}")
    print(f"Open it with:   .venv/Scripts/python.exe -m viztracer --open {report_path}")
    if open_report:
        from viztracer.viewer import viewer_main

        sys.argv = ["vizviewer", "--once", str(report_path)]
        viewer_main()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--view",
        choices=("tree", "timeline"),
        default="tree",
        help="tree = pyinstrument call tree (default); timeline = viztracer Perfetto timeline",
    )
    parser.add_argument("--open", action="store_true", help="open the rendered report in the browser")
    parser.add_argument(
        "--cold",
        action="store_true",
        help="measure cold-FS boots: flush the file cache (self-elevates via UAC) and run --runs fresh boots",
    )
    parser.add_argument("--runs", type=int, default=5, help="number of cold boots to run (default 5)")
    parser.add_argument(
        "--single",
        action="store_true",
        help="internal: run exactly one un-profiled boot and print its elapsed milliseconds",
    )
    parser.add_argument(
        "--cold-worker",
        action="store_true",
        help="internal: elevated headless worker that flushes the cache and boots, streaming to the log",
    )
    arguments = parser.parse_args()

    if arguments.single:
        elapsed = _drive_boot_until_window_shown()
        print(f"{_ELAPSED_PREFIX}{elapsed * 1000:.1f}")
        return

    if arguments.cold_worker:
        if not _is_admin():
            raise SystemExit("--cold-worker must run elevated.")
        _run_cold_worker(arguments.runs)
        return

    if arguments.cold:
        _measure_cold_boots(arguments.runs)
        return

    if arguments.view == "tree":
        _profile_with_pyinstrument(arguments.open)
    else:
        _profile_with_viztracer(arguments.open)


if __name__ == "__main__":
    main()
