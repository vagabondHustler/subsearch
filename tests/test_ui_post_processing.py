from pathlib import Path

import pytest


@pytest.fixture
def post_process_workspace(monkeypatch):
    from subsearch.ui.services import post_processing

    monkeypatch.setattr(post_processing.WORKSPACE, "download_directory", Path("downloads"), raising=False)
    monkeypatch.setattr(post_processing.WORKSPACE, "extraction_directory", Path("subs"), raising=False)


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
    monkeypatch.setattr(
        post_processing.subtitle_selection, "autoload_rename", lambda search_term, src: src / "renamed.srt"
    )
    monkeypatch.setattr(post_processing.file_system, "move_and_replace", lambda src, dst: None)
    monkeypatch.setattr(post_processing.file_system, "create_path_from_string", lambda *args, **kwargs: Path("target"))
    worker = post_processing._PostProcessWorker(rename=rename, store=SettingsStore(), subtitle=_make_subtitle())
    return worker.execute()


def test_unpack_and_move_stops_at_extraction_directory(monkeypatch, post_process_workspace) -> None:
    delivered = _run_unpack_worker(monkeypatch, rename=False, extracted_count=2)

    assert delivered == 2


def test_unpack_warns_when_archive_yields_nothing(monkeypatch, post_process_workspace) -> None:
    delivered = _run_unpack_worker(monkeypatch, rename=False, extracted_count=0)

    assert delivered == 0


def test_unpack_extracts_only_the_selected_subtitle(monkeypatch, post_process_workspace) -> None:
    from subsearch.ui.services import post_processing
    from subsearch.ui.state.store import SettingsStore

    subtitle = _make_subtitle()
    seen_calls: list[tuple[str, Path, Path]] = []

    def record_extraction(subtitle_id: str, src: Path, dst: Path) -> int:
        seen_calls.append((subtitle_id, src, dst))
        return 1

    monkeypatch.setattr(post_processing.file_system, "extract_subtitle_by_id", record_extraction)
    worker = post_processing._PostProcessWorker(rename=False, store=SettingsStore(), subtitle=subtitle)
    worker.execute()

    assert seen_calls == [(subtitle.subtitle_id, Path("downloads"), Path("subs"))]


def test_rename_and_place_delivers_to_target(monkeypatch, tmp_path, post_process_workspace) -> None:
    from subsearch.ui.services import post_processing
    from subsearch.ui.state.store import SettingsStore

    target_dir = tmp_path / "target"
    target_dir.mkdir()
    monkeypatch.setattr(post_processing.file_system, "extract_subtitle_by_id", lambda subtitle_id, src, dst: 1)
    monkeypatch.setattr(
        post_processing.subtitle_selection, "autoload_rename", lambda search_term, src: src / "renamed.srt"
    )
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
