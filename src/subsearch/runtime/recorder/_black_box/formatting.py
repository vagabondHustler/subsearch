import logging

from subsearch.runtime.recorder._black_box.recorded_entry import RecordedEntry
from subsearch.runtime.recorder.config import LOG_DATE_FORMAT, LOG_FORMAT


class EntryFormatter:
    def __init__(self) -> None:
        self._log_formatter = logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT)

    def console_form(self, entry: RecordedEntry) -> str:
        return entry.message

    def log_form(self, entry: RecordedEntry) -> str:
        log_record = logging.LogRecord(
            name=entry.module,
            level=self._level_number(entry.level),
            pathname=entry.module,
            lineno=entry.line_number,
            msg=entry.message,
            args=None,
            exc_info=None,
        )
        log_record.module = entry.module
        log_record.created = entry.captured_at
        return self._log_formatter.format(log_record)

    @staticmethod
    def _level_number(level: str) -> int:
        return _LEVEL_NUMBERS.get(level, logging.INFO)


_LEVEL_NUMBERS = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL,
    "banner": logging.INFO,
}
