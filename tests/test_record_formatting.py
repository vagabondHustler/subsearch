import re

from subsearch.runtime.recorder._black_box.formatting import EntryFormatter
from subsearch.runtime.recorder._black_box.recorded_entry import RecordedEntry
from subsearch.runtime.recorder.config import LogLevel


def _entry(level: LogLevel = LogLevel.INFO) -> RecordedEntry:
    return RecordedEntry(lines=("hello world",), level=level, module="pipeline", line_number=42, captured_at=0.0)


def test_console_form_is_message_only() -> None:
    formatter = EntryFormatter()
    assert formatter.console_form(_entry()) == "hello world"


def test_log_form_carries_level_and_module_lineno() -> None:
    formatter = EntryFormatter()
    log_form = formatter.log_form(_entry(LogLevel.WARNING))
    # asctime is HH:MM:SS, then level, then module:lineno, then message
    assert re.match(r"\d{2}:\d{2}:\d{2} WARNING  pipeline:42 hello world", log_form)


def test_console_and_log_forms_differ() -> None:
    formatter = EntryFormatter()
    entry = _entry()
    assert formatter.console_form(entry) != formatter.log_form(entry)
    assert formatter.console_form(entry) in formatter.log_form(entry)
