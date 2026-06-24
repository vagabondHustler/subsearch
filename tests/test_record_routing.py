from subsearch.runtime.recorder.config import LogLevel
from subsearch.runtime.recorder._black_box.formatting import EntryFormatter
from subsearch.runtime.recorder._black_box.recorded_entry import RecordedEntry
from subsearch.runtime.recorder._black_box.routing import EntryRouter


class _FakeConsoleOutput:
    def __init__(self) -> None:
        self.written: list[str] = []

    def write_entry(self, entry: RecordedEntry, console_form: str) -> None:
        self.written.append(console_form)

    def tick(self) -> None:
        pass

    def close(self) -> None:
        pass


class _FakeLogFileOutput:
    def __init__(self) -> None:
        self.written: list[str] = []

    def write(self, text: str) -> None:
        self.written.append(text)


class _FakeCrashFileOutput:
    def __init__(self) -> None:
        self.sessions: list[str] = []

    def write_session(self, session: str) -> None:
        self.sessions.append(session)


def _entry(level: LogLevel) -> RecordedEntry:
    return RecordedEntry(lines=("msg",), level=level, module="m", line_number=1, captured_at=0.0)


def _router():
    console = _FakeConsoleOutput()
    log_file = _FakeLogFileOutput()
    crash_file = _FakeCrashFileOutput()
    router = EntryRouter(EntryFormatter(), console, log_file, crash_file)  # type: ignore[arg-type]
    return router, console, log_file, crash_file


def test_banner_goes_to_console_not_log() -> None:
    router, console, log_file, _ = _router()
    router.route(_entry(LogLevel.PHASE))
    assert console.written == ["msg"]
    assert log_file.written == []


def test_warning_and_error_reach_console_and_log() -> None:
    router, console, log_file, _ = _router()
    router.route(_entry(LogLevel.WARNING))
    router.route(_entry(LogLevel.ERROR))
    assert console.written == ["msg", "msg"]
    assert len(log_file.written) == 2


def test_info_reaches_console_as_transient_and_log() -> None:
    router, console, log_file, _ = _router()
    router.route(_entry(LogLevel.INFO))
    assert console.written == ["msg"]
    assert len(log_file.written) == 1


def test_debug_is_log_only() -> None:
    router, console, log_file, _ = _router()
    router.route(_entry(LogLevel.DEBUG))
    assert console.written == []
    assert len(log_file.written) == 1


def test_route_crash_reaches_crash_output_only() -> None:
    router, console, log_file, crash_file = _router()
    router.route_crash("boom")
    assert crash_file.sessions == ["boom"]
    assert console.written == []
    assert log_file.written == []
