from pathlib import Path

import pytest


@pytest.fixture
def captured_events(monkeypatch):
    from subsearch.ui.services import post_processing

    events: list[tuple[str, dict]] = []
    monkeypatch.setattr(post_processing.log, "event", lambda key, **values: events.append((key, values)))
    monkeypatch.setattr(post_processing.WORKSPACE, "download_directory", Path("downloads"), raising=False)
    monkeypatch.setattr(post_processing.WORKSPACE, "extraction_directory", Path("subs"), raising=False)
    return events


def _make_subtitle():
    from subsearch.runtime.models import Subtitle

    return Subtitle(
        token_result=0,
        provider_name="provider",
        subtitle_name="subtitle",
        download_url="https://example.test/subtitle.zip",
        request_data={},
    )


def _run_unpack_worker(monkeypatch, rename: bool, extracted_count: int):
    from subsearch.ui.services import post_processing
    from subsearch.ui.state.store import SettingsStore

    monkeypatch.setattr(
        post_processing.file_system, "extract_subtitle_by_id", lambda subtitle_id, src, dst: extracted_count
    )
    monkeypatch.setattr(post_processing.file_system, "autoload_rename", lambda search_term, src: src / "renamed.srt")
    monkeypatch.setattr(post_processing.file_system, "move_and_replace", lambda src, dst: None)
    monkeypatch.setattr(post_processing.file_system, "create_path_from_string", lambda *args, **kwargs: Path("target"))
    worker = post_processing._PostProcessWorker(rename=rename, store=SettingsStore(), subtitle=_make_subtitle())
    return worker.execute()


def _event_keys(events) -> list[str]:
    return [key for key, _ in events]


def test_unpack_and_move_stops_at_extraction_directory(monkeypatch, captured_events) -> None:
    delivered = _run_unpack_worker(monkeypatch, rename=False, extracted_count=2)

    assert delivered == 2
    completed = next(values for key, values in captured_events if key == "post_processing_completed")
    assert completed["destination"] == Path("subs")
    assert completed["moved"] == 2


def test_unpack_warns_when_archive_yields_nothing(monkeypatch, captured_events) -> None:
    delivered = _run_unpack_worker(monkeypatch, rename=False, extracted_count=0)

    assert delivered == 0
    keys = _event_keys(captured_events)
    assert "post_processing_no_files" in keys
    assert "post_processing_completed" not in keys
    warning = next(values for key, values in captured_events if key == "post_processing_no_files")
    assert warning["level"] == "warning"


def test_unpack_extracts_only_the_selected_subtitle(monkeypatch, captured_events) -> None:
    from subsearch.ui.services import post_processing
    from subsearch.ui.state.store import SettingsStore

    subtitle = _make_subtitle()
    seen_calls: list[tuple[str, Path, Path]] = []
    monkeypatch.setattr(
        post_processing.file_system,
        "extract_subtitle_by_id",
        lambda subtitle_id, src, dst: (seen_calls.append((subtitle_id, src, dst)), 1)[1],
    )
    worker = post_processing._PostProcessWorker(rename=False, store=SettingsStore(), subtitle=subtitle)
    worker.execute()

    assert seen_calls == [(subtitle.subtitle_id, Path("downloads"), Path("subs"))]


def test_rename_and_place_delivers_to_target(monkeypatch, tmp_path, captured_events) -> None:
    from subsearch.ui.services import post_processing
    from subsearch.ui.state.store import SettingsStore

    target_dir = tmp_path / "target"
    target_dir.mkdir()
    monkeypatch.setattr(post_processing.file_system, "extract_subtitle_by_id", lambda subtitle_id, src, dst: 1)
    monkeypatch.setattr(post_processing.file_system, "autoload_rename", lambda search_term, src: src / "renamed.srt")
    placed: list[tuple[Path, Path]] = []

    def fake_move(source_file, destination_directory):
        placed.append((source_file, destination_directory))
        (destination_directory / source_file.name).write_text("subtitle")

    monkeypatch.setattr(post_processing.file_system, "move_and_replace", fake_move)
    monkeypatch.setattr(post_processing.file_system, "create_path_from_string", lambda *args, **kwargs: target_dir)
    worker = post_processing._PostProcessWorker(rename=True, store=SettingsStore(), subtitle=_make_subtitle())
    delivered = worker.execute()

    assert delivered == 1
    assert placed == [(Path("subs") / "renamed.srt", target_dir)]
    completed = next(values for key, values in captured_events if key == "post_processing_completed")
    assert completed["destination"] == target_dir
