from subsearch.runtime.recorder import LogLevel


def _banner_messages(records):
    return [message for message, level in records if level is LogLevel.PHASE]


def _patch_window(monkeypatch, records):
    from subsearch.ui import entrypoint

    class FakeWindow:
        def __init__(self, *args, **kwargs) -> None:
            self.manual_search_interface = type(
                "Interface", (), {"downloaded": [], "placed_best_next_to_video": False}
            )()

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

    def record_capture(*lines, level=LogLevel.INFO):
        for line in lines:
            records.append((line, level))

    monkeypatch.setattr(entrypoint, "capture", record_capture)
    monkeypatch.setattr(entrypoint, "phase", lambda *lines: record_capture(*lines, level=LogLevel.PHASE))
    return entrypoint


def test_open_settings_window_starts_waiting_banner_when_not_searching_immediately(monkeypatch) -> None:
    records: list[tuple] = []
    entrypoint = _patch_window(monkeypatch, records)

    entrypoint.open_settings_window(search_job_factory=lambda *_: None, start_search_immediately=False)

    assert "Idle" in _banner_messages(records)


def test_open_settings_window_defers_waiting_banner_to_search_worker_on_immediate_search(monkeypatch) -> None:
    records: list[tuple] = []
    entrypoint = _patch_window(monkeypatch, records)

    entrypoint.open_settings_window(search_job_factory=lambda *_: None, start_search_immediately=True)

    # The search worker owns the banner sequence; the entrypoint must not start its
    # own "Idle" banner or it gets torn down.
    assert "Idle" not in _banner_messages(records)
