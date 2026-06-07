import threading

import pytest

from subsearch.ui import warmup


@pytest.fixture(autouse=True)
def reset_warmup_state():
    warmup._warmup_thread = None
    yield
    if warmup._warmup_thread is not None:
        warmup._warmup_thread.join()
    warmup._warmup_thread = None


def test_await_warmup_is_noop_when_not_started():
    warmup.await_warmup()
    assert warmup._warmup_thread is None


def test_start_warmup_spawns_a_thread():
    warmup.start_warmup()
    assert isinstance(warmup._warmup_thread, threading.Thread)


def test_start_warmup_is_idempotent():
    warmup.start_warmup()
    first_thread = warmup._warmup_thread
    warmup.start_warmup()
    assert warmup._warmup_thread is first_thread


def test_warmup_thread_is_daemon():
    warmup.start_warmup()
    assert warmup._warmup_thread.daemon is True


def test_await_warmup_joins_the_thread():
    warmup.start_warmup()
    warmup.await_warmup()
    assert warmup._warmup_thread.is_alive() is False


def test_start_warmup_imports_the_application_module():
    import sys

    sys.modules.pop("subsearch.ui.application", None)
    warmup.start_warmup()
    warmup.await_warmup()
    assert "subsearch.ui.application" in sys.modules
