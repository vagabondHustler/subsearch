from unittest.mock import patch

import pytest

from subsearch.decorators import process_guard


def _terminal_messages(messages: list[str]) -> list[str]:
    return [message for message in messages if message.startswith("Exited")]


def _run_guarded(func) -> list[str]:
    recorded: list[str] = []

    def record(*lines, **kwargs):
        recorded.extend(lines)

    with (
        patch.object(process_guard, "capture", side_effect=record),
        patch.object(process_guard, "flush_crash"),
        patch.object(process_guard, "_run_with_mutex", side_effect=lambda f, *a, **k: f()),
    ):
        guarded = process_guard.apply_mutex(func)
        try:
            guarded()
        except RuntimeError:
            pass
    return recorded


def test_clean_exit_records_no_terminal_message() -> None:
    # the elapsed run time is now reported by the recorder's "Exiting" phase, not here
    recorded = _run_guarded(lambda: None)
    assert _terminal_messages(recorded) == []


def test_unhandled_exception_records_crash_message() -> None:
    def boom() -> None:
        raise RuntimeError("boom")

    recorded = _run_guarded(boom)
    terminal = _terminal_messages(recorded)
    assert len(terminal) == 1
    assert terminal[0].endswith("following an unhandled exception")


def test_unhandled_exception_flushes_crash() -> None:
    def boom() -> None:
        raise RuntimeError("boom")

    with (
        patch.object(process_guard, "capture"),
        patch.object(process_guard, "flush_crash") as flush_crash,
        patch.object(process_guard, "_run_with_mutex", side_effect=lambda f, *a, **k: f()),
    ):
        guarded = process_guard.apply_mutex(boom)
        with pytest.raises(RuntimeError):
            guarded()
    flush_crash.assert_called_once()


def test_unhandled_exception_propagates() -> None:
    def boom() -> None:
        raise RuntimeError("boom")

    with (
        patch.object(process_guard, "capture"),
        patch.object(process_guard, "flush_crash"),
        patch.object(process_guard, "_run_with_mutex", side_effect=lambda f, *a, **k: f()),
    ):
        guarded = process_guard.apply_mutex(boom)
        with pytest.raises(RuntimeError):
            guarded()
