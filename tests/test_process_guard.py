from unittest.mock import patch

import pytest

from subsearch.decorators import process_guard
from subsearch.runtime.logging.events import LogEvent


def _terminal_events(recorded_events: list[LogEvent]) -> list[LogEvent]:
    return [event for event in recorded_events if event in (LogEvent.PIPELINE_FINISHED, LogEvent.PIPELINE_CRASHED)]


def _run_guarded(func):
    recorded: list[LogEvent] = []

    def record(event, *args, **kwargs):
        recorded.append(event)

    with (
        patch.object(process_guard.log, "event", side_effect=record),
        patch.object(process_guard.log, "end_banner"),
        patch.object(process_guard, "_run_with_mutex", side_effect=lambda f, *a, **k: f()),
    ):
        guarded = process_guard.apply_mutex(func)
        try:
            guarded()
        except RuntimeError:
            pass
    return recorded


def test_clean_exit_logs_pipeline_finished() -> None:
    recorded = _run_guarded(lambda: None)
    assert _terminal_events(recorded) == [LogEvent.PIPELINE_FINISHED]


def test_unhandled_exception_logs_pipeline_crashed() -> None:
    def boom() -> None:
        raise RuntimeError("boom")

    recorded = _run_guarded(boom)
    assert _terminal_events(recorded) == [LogEvent.PIPELINE_CRASHED]


def test_unhandled_exception_propagates() -> None:
    def boom() -> None:
        raise RuntimeError("boom")

    with (
        patch.object(process_guard.log, "event"),
        patch.object(process_guard.log, "end_banner"),
        patch.object(process_guard, "_run_with_mutex", side_effect=lambda f, *a, **k: f()),
    ):
        guarded = process_guard.apply_mutex(boom)
        with pytest.raises(RuntimeError):
            guarded()
