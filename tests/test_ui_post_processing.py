from pathlib import Path

import pytest


@pytest.fixture
def captured_events(monkeypatch):
    from subsearch.ui.services import post_processing

    events: list[tuple[str, dict]] = []
    monkeypatch.setattr(post_processing.log, "event", lambda key, **values: events.append((key, values)))
    monkeypatch.setattr(post_processing.VIDEO_FILE, "download_directory", Path("."), raising=False)
    monkeypatch.setattr(post_processing.VIDEO_FILE, "extraction_directory", Path("."), raising=False)
    return events


def _run_move_worker(monkeypatch, extracted_count: int, moved_count: int):
    from subsearch.ui.services import post_processing
    from subsearch.ui.state.store import SettingsStore

    monkeypatch.setattr(post_processing.file_system, "extract_files_in_dir", lambda src, dst: extracted_count)
    monkeypatch.setattr(post_processing.file_system, "move_all", lambda src, dst: moved_count)
    monkeypatch.setattr(post_processing.file_system, "create_path_from_string", lambda *args, **kwargs: Path("."))
    worker = post_processing._PostProcessWorker(rename=False, store=SettingsStore())
    worker.execute()


def _event_keys(events) -> list[str]:
    return [key for key, _ in events]


def test_post_processing_completed_reports_real_counts(monkeypatch, captured_events) -> None:
    _run_move_worker(monkeypatch, extracted_count=3, moved_count=2)

    keys = _event_keys(captured_events)
    assert "post_processing_completed" in keys
    assert "post_processing_no_files" not in keys
    completed = next(values for key, values in captured_events if key == "post_processing_completed")
    assert completed["extracted"] == 3
    assert completed["moved"] == 2


def test_post_processing_warns_when_nothing_moved(monkeypatch, captured_events) -> None:
    _run_move_worker(monkeypatch, extracted_count=1, moved_count=0)

    keys = _event_keys(captured_events)
    assert "post_processing_no_files" in keys
    assert "post_processing_completed" in keys
    warning = next(values for key, values in captured_events if key == "post_processing_no_files")
    assert warning["level"] == "warning"
    assert warning["moved"] == 0


def test_post_processing_warns_when_nothing_extracted(monkeypatch, captured_events) -> None:
    _run_move_worker(monkeypatch, extracted_count=0, moved_count=0)

    assert "post_processing_no_files" in _event_keys(captured_events)
