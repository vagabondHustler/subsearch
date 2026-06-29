from pathlib import Path
from types import SimpleNamespace

from subsearch.core.pipeline import SearchPipeline
from subsearch.io import file_system
from subsearch.runtime.config import composition
from subsearch.runtime.download_history import DownloadHistory
from subsearch.runtime.models import Subtitle, SubtitleStatus


def _subtitle(name: str, url: str) -> Subtitle:
    return Subtitle(
        token_result=100,
        provider_name="gestdown",
        subtitle_name=name,
        download_url=url,
        request_data={},
    )


def _pipeline(downloads_per_provider: int = 4) -> SearchPipeline:
    pipeline = SearchPipeline.__new__(SearchPipeline)
    pipeline.bootstrap = SimpleNamespace(  # type: ignore[attr-defined]
        api_calls_made={},
        app_config=SimpleNamespace(downloads_per_provider=downloads_per_provider),
    )
    return pipeline


def test_identical_bytes_keep_one_skip_second(tmp_path, monkeypatch) -> None:
    history = DownloadHistory(tmp_path / "files_tracked.json")
    monkeypatch.setattr(composition.WORKSPACE, "download_directory", tmp_path, raising=False)

    shared_hash = "shared-hash"
    calls = iter(
        [
            file_system.DownloadedSubtitle(tmp_path / "first.srt", shared_hash),
            file_system.DownloadedSubtitle(tmp_path / "second.srt", shared_hash),
        ]
    )
    monkeypatch.setattr(file_system, "download_subtitle", lambda *args, **kwargs: next(calls))

    pipeline = _pipeline()
    pipeline.bootstrap.api_calls_made["gestdown"] = 0
    first = _subtitle("first", "u-first")
    second = _subtitle("second", "u-second")

    pipeline._download_accepted_subtitle(first, 2, history)
    pipeline._download_accepted_subtitle(second, 2, history)

    assert first.status is SubtitleStatus.AUTO_DOWNLOAD
    assert second.status is not SubtitleStatus.AUTO_DOWNLOAD
    assert pipeline.bootstrap.api_calls_made["gestdown"] == 1
    assert history.take_pending_deletion() == [tmp_path / "second.srt"]
    assert history.was_downloaded_hash(shared_hash) is True
