from types import SimpleNamespace

from subsearch.core.pipeline import SearchPipeline


class RecordingTray:
    def __init__(self) -> None:
        self.shown: list[tuple[str, str]] = []

    def display_toast(self, title: str, message: str) -> None:
        self.shown.append((title, message))


def _pipeline_with_bootstrap() -> tuple[SearchPipeline, RecordingTray]:
    tray = RecordingTray()
    bootstrap = SimpleNamespace(pending_notifications=[], system_tray=tray)
    pipeline = SearchPipeline.__new__(SearchPipeline)
    pipeline.bootstrap = bootstrap  # type: ignore[attr-defined]
    return pipeline, tray


def test_missing_api_key_queues_instead_of_toasting() -> None:
    pipeline, tray = _pipeline_with_bootstrap()

    pipeline._notify_missing_api_key("subsource")

    assert tray.shown == []
    assert pipeline.bootstrap.pending_notifications == [
        ("subsource skipped", "Add your subsource API key in settings to search subsource.")
    ]


def test_present_pending_notifications_drains_in_order_and_clears() -> None:
    pipeline, tray = _pipeline_with_bootstrap()
    pipeline.bootstrap.pending_notifications.extend([("a", "1"), ("b", "2")])

    pipeline.present_pending_notifications()

    assert tray.shown == [("a", "1"), ("b", "2")]
    assert pipeline.bootstrap.pending_notifications == []
