from datetime import datetime, timedelta
from pathlib import Path

from subsearch.runtime.download_history import DownloadHistory


def _history(tmp_path: Path) -> DownloadHistory:
    return DownloadHistory(tmp_path / "files_tracked.json")


def test_record_then_url_and_hash_hit(tmp_path) -> None:
    history = _history(tmp_path)
    history.record("hash-a", "https://example.test/a", tmp_path / "a.srt")

    assert history.was_downloaded_url("https://example.test/a") is True
    assert history.was_downloaded_hash("hash-a") is True
    assert history.was_downloaded_url("https://example.test/b") is False
    assert history.was_downloaded_hash("hash-b") is False


def test_history_persists_across_instances(tmp_path) -> None:
    history = _history(tmp_path)
    history.record("hash-a", "https://example.test/a", tmp_path / "a.srt")

    reloaded = _history(tmp_path)
    assert reloaded.was_downloaded_hash("hash-a") is True


def test_pending_deletion_round_trip(tmp_path) -> None:
    history = _history(tmp_path)
    history.mark_pending_deletion(tmp_path / "dupe.srt")
    history.mark_pending_deletion(tmp_path / "dupe.srt")  # idempotent

    taken = history.take_pending_deletion()
    assert taken == [tmp_path / "dupe.srt"]
    assert history.take_pending_deletion() == []


def test_increment_run_count(tmp_path) -> None:
    history = _history(tmp_path)
    assert history.run_count == 0
    history.increment_run_count()
    history.increment_run_count()
    assert history.run_count == 2


def test_prune_by_days(tmp_path) -> None:
    history = _history(tmp_path)
    history.record("stale", "u-stale", tmp_path / "stale.srt")
    history._records[0].recorded_on = (datetime.now() - timedelta(days=30)).date().isoformat()
    history.record("fresh", "u-fresh", tmp_path / "fresh.srt")

    history.prune(days=7, runs=100)

    assert history.was_downloaded_hash("fresh") is True
    assert history.was_downloaded_hash("stale") is False


def test_prune_by_runs(tmp_path) -> None:
    history = _history(tmp_path)
    history.increment_run_count()  # run 1
    history.record("old", "u-old", tmp_path / "old.srt")
    for _ in range(20):
        history.increment_run_count()
    history.record("recent", "u-recent", tmp_path / "recent.srt")

    history.prune(days=3650, runs=10)

    assert history.was_downloaded_hash("recent") is True
    assert history.was_downloaded_hash("old") is False
