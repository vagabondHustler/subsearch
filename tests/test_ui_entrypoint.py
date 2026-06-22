from subsearch.runtime.logging.events import LogEvent


def _spinner_titles(events):
    return [title for event_key, title in events if event_key == LogEvent.SPINNER]


def _patch_window(monkeypatch, events):
    from subsearch.ui.application import entrypoint
    from subsearch.runtime.logging.logger import log

    class FakeWindow:
        def __init__(self, *args, **kwargs) -> None:
            self.manual_search_interface = type("Interface", (), {"downloaded": []})()

        def show(self) -> None:
            pass

    class FakeApplication:
        def setStyleSheet(self, *_args) -> None:
            pass

        def exec(self) -> None:
            pass

    monkeypatch.setattr(entrypoint, "SettingsWindow", FakeWindow)
    monkeypatch.setattr(entrypoint, "get_application", lambda: FakeApplication())
    monkeypatch.setattr(entrypoint, "setTheme", lambda *_a: None)
    monkeypatch.setattr(entrypoint, "setThemeColor", lambda *_a: None)
    monkeypatch.setattr(entrypoint, "force_fixed_accent_color", lambda: None)
    monkeypatch.setattr(entrypoint, "qInstallMessageHandler", lambda *_a: None)
    monkeypatch.setattr(entrypoint.warmup, "await_warmup", lambda: None)

    original_event = log.event

    def record_event(event_key, level="info", **values):
        events.append((event_key, values.get("title")))
        if event_key != LogEvent.SPINNER:
            return original_event(event_key, level, **values)

    monkeypatch.setattr(log, "event", record_event)
    return entrypoint


def test_open_settings_window_starts_waiting_banner_when_not_searching_immediately(monkeypatch) -> None:
    events: list[tuple] = []
    entrypoint = _patch_window(monkeypatch, events)

    entrypoint.open_settings_window(search_job_factory=lambda *_: None, start_search_immediately=False)

    assert "Waiting for user inputs" in _spinner_titles(events)


def test_open_settings_window_defers_waiting_banner_to_search_worker_on_immediate_search(monkeypatch) -> None:
    events: list[tuple] = []
    entrypoint = _patch_window(monkeypatch, events)

    entrypoint.open_settings_window(search_job_factory=lambda *_: None, start_search_immediately=True)

    # The search worker owns the banner sequence; the entrypoint must not start its
    # own "Waiting for user inputs" or it gets torn down with a spurious done-title.
    assert "Waiting for user inputs" not in _spinner_titles(events)
