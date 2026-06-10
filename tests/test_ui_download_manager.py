import pytest

from subsearch.runtime.models.model import Subtitle, SubtitleStatus


def make_subtitle(
    name: str, token_result: int, status: SubtitleStatus, download_url: str = "http://example"
) -> Subtitle:
    return Subtitle(
        token_result=token_result,
        provider_name="opensubtitles",
        subtitle_name=name,
        download_url=download_url,
        request_data={},
        status=status,
    )


@pytest.fixture
def download_environment(monkeypatch, tmp_path):
    from subsearch.io import file_system
    from subsearch.runtime.config import constants

    downloaded = []
    monkeypatch.setattr(file_system, "download_subtitle", lambda subtitle, number, total: downloaded.append(subtitle))
    monkeypatch.setattr(file_system, "extract_files_in_dir", lambda src, dst, extension=".zip": None)
    monkeypatch.setattr(constants.VIDEO_FILE, "tmp_dir", tmp_path / "tmp", raising=False)
    (tmp_path / "tmp").mkdir()
    return downloaded


def build_interface(subtitles, qtbot):
    from subsearch.ui.cards.download_manager import DownloadManagerInterface
    from subsearch.ui.services.subtitle_downloads import SubtitleDownloadService
    from subsearch.ui.state.store import SettingsStore
    from subsearch.ui.state.tasks import TaskRunner

    task_runner = TaskRunner()
    service = SubtitleDownloadService(task_runner)
    interface = DownloadManagerInterface(SettingsStore(), service, subtitles)
    qtbot.addWidget(interface)
    return interface, task_runner


def test_accepted_subtitles_download_when_manager_opens(qtbot, download_environment) -> None:
    accepted = make_subtitle("Accepted.Sub", 95, SubtitleStatus.ACCEPTED)
    rejected = make_subtitle("Rejected.Sub", 10, SubtitleStatus.BELOW_THRESHOLD)

    interface, task_runner = build_interface([accepted, rejected], qtbot)
    try:
        qtbot.waitUntil(lambda: accepted in interface.downloaded, timeout=5000)
    finally:
        task_runner.shutdown()

    assert accepted.status is SubtitleStatus.MANUALLY_DOWNLOADED
    assert download_environment == [accepted]
    assert rejected not in interface.downloaded
    assert rejected.status is SubtitleStatus.BELOW_THRESHOLD


def test_auto_downloaded_subtitles_render_as_downloaded_without_redownload(qtbot, download_environment) -> None:
    auto_downloaded = make_subtitle("Auto.Sub", 96, SubtitleStatus.AUTO_DOWNLOADED)

    interface, task_runner = build_interface([auto_downloaded], qtbot)
    task_runner.shutdown()

    assert auto_downloaded in interface.downloaded
    assert download_environment == []


def test_subtitle_without_url_fails_on_click(qtbot, download_environment) -> None:
    no_url = make_subtitle("NoUrl.Sub", 50, SubtitleStatus.BELOW_THRESHOLD, download_url="")

    interface, task_runner = build_interface([no_url], qtbot)
    try:
        item = interface.list_widget.item(0)
        interface._on_item_clicked(item)
    finally:
        task_runner.shutdown()

    assert no_url in interface.failed
    assert no_url.status is SubtitleStatus.DOWNLOAD_FAILED
