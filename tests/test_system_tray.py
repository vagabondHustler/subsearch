import threading

import pytest

from subsearch.ui import system_tray
from subsearch.ui.qt_application import get_application
from subsearch.ui.system_tray import SystemTray


@pytest.fixture
def tray(monkeypatch: pytest.MonkeyPatch) -> SystemTray:
    get_application()
    monkeypatch.setattr(system_tray, "notifications_allowed", lambda: True)
    return SystemTray(enabled=True, display_duration_ms=0, play_sound=False)


def test_display_toast_from_worker_thread_is_rejected(tray: SystemTray) -> None:
    failure: list[BaseException] = []

    def worker() -> None:
        try:
            tray.display_toast("title", "message")
        except BaseException as error:  # noqa: BLE001 - capture the guard for assertion
            failure.append(error)

    thread = threading.Thread(target=worker)
    thread.start()
    thread.join(timeout=5)

    assert not thread.is_alive()
    assert len(failure) == 1
    assert isinstance(failure[0], AssertionError)


def test_display_toast_disabled_is_noop_on_any_thread(monkeypatch: pytest.MonkeyPatch) -> None:
    get_application()
    monkeypatch.setattr(system_tray, "notifications_allowed", lambda: True)
    disabled = SystemTray(enabled=False, display_duration_ms=0, play_sound=False)

    returned_cleanly: list[bool] = []

    def worker() -> None:
        disabled.display_toast("title", "message")
        returned_cleanly.append(True)

    thread = threading.Thread(target=worker)
    thread.start()
    thread.join(timeout=5)

    assert returned_cleanly == [True]
