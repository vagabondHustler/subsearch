from pathlib import Path

from subsearch.runtime.recorder._black_box.standard_error.crash_file_output import (
    CrashFileOutput,
)
from subsearch.runtime.recorder._black_box.standard_out.log_file_output import (
    RotatingLogFileOutput,
)
from subsearch.runtime.recorder.config import SESSION_SEPARATOR


def test_log_file_writes_session_separator_once(tmp_path: Path) -> None:
    # not "log.log": the autouse recorder fixture writes its own session to tmp_path/log.log
    output = RotatingLogFileOutput(tmp_path / "isolated.log", max_bytes=1_000_000)
    output.write("first")
    output.write("second")
    contents = (tmp_path / "isolated.log").read_text(encoding="utf-8")
    assert contents.count(SESSION_SEPARATOR) == 1
    assert "first" in contents
    assert "second" in contents


def test_log_file_is_size_capped(tmp_path: Path) -> None:
    output = RotatingLogFileOutput(tmp_path / "log.log", max_bytes=200)
    for index in range(100):
        output.write(f"line {index} " + "x" * 40)
    assert (tmp_path / "log.log").stat().st_size <= 200


def test_crash_output_writes_session_delimited_block(tmp_path: Path) -> None:
    output = CrashFileOutput(tmp_path / "crash.log", max_bytes=1_000_000, clear_every_runs=5)
    output.write_session("first crash\nTraceback ...")
    output.write_session("second crash\nTraceback ...")
    contents = (tmp_path / "crash.log").read_text(encoding="utf-8")
    assert contents.count(SESSION_SEPARATOR) == 2
    assert "first crash" in contents
    assert "second crash" in contents


def test_crash_output_skips_empty_session(tmp_path: Path) -> None:
    output = CrashFileOutput(tmp_path / "crash.log", max_bytes=1_000_000, clear_every_runs=5)
    output.write_session("   \n  ")
    assert not (tmp_path / "crash.log").exists()


def test_crash_output_clears_every_n_runs(tmp_path: Path) -> None:
    output = CrashFileOutput(tmp_path / "crash.log", max_bytes=1_000_000, clear_every_runs=5)
    for index in range(12):
        output.write_session(f"crash {index}")
    contents = (tmp_path / "crash.log").read_text(encoding="utf-8")
    # the 11th run (index 10, count 10 % 5 == 0) clears, so only runs 11 and 12 remain
    assert "crash 11" in contents
    assert "crash 0" not in contents


def test_crash_output_is_size_capped(tmp_path: Path) -> None:
    output = CrashFileOutput(tmp_path / "crash.log", max_bytes=200, clear_every_runs=1000)
    for index in range(50):
        output.write_session(f"crash {index} " + "x" * 50)
    assert (tmp_path / "crash.log").stat().st_size <= 200
