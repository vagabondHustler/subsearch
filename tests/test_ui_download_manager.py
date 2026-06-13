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
    monkeypatch.setattr(
        file_system, "download_subtitle", lambda subtitle, number, total, tmp_dir: downloaded.append(subtitle)
    )
    monkeypatch.setattr(file_system, "extract_files_in_dir", lambda src, dst, extension=".zip": None)
    monkeypatch.setattr(constants.VIDEO_FILE, "tmp_dir", tmp_path / "tmp", raising=False)
    (tmp_path / "tmp").mkdir()
    return downloaded


def build_interface(subtitles, qtbot):
    from subsearch.ui.cards.download_manager import ManualSearchInterface
    from subsearch.ui.services.post_processing import PostProcessingService
    from subsearch.ui.services.subtitle_downloads import SubtitleDownloadService
    from subsearch.ui.services.video_file import VideoFileService
    from subsearch.ui.state.store import SettingsStore
    from subsearch.ui.state.tasks import TaskRunner

    task_runner = TaskRunner()
    download_service = SubtitleDownloadService(task_runner)
    post_processing_service = PostProcessingService(task_runner)
    interface = ManualSearchInterface(
        SettingsStore(), download_service, post_processing_service, VideoFileService(), subtitles
    )
    qtbot.addWidget(interface)
    return interface, task_runner


def test_no_subtitle_downloads_until_clicked(qtbot, download_environment) -> None:
    accepted = make_subtitle("Accepted.Sub", 95, SubtitleStatus.ACCEPTED)
    rejected = make_subtitle("Rejected.Sub", 10, SubtitleStatus.BELOW_THRESHOLD)

    _, task_runner = build_interface([accepted, rejected], qtbot)
    task_runner.shutdown()

    assert download_environment == []
    assert accepted.status is SubtitleStatus.ACCEPTED
    assert rejected.status is SubtitleStatus.BELOW_THRESHOLD


def test_clicking_subtitle_downloads_it(qtbot, download_environment) -> None:
    accepted = make_subtitle("Accepted.Sub", 95, SubtitleStatus.ACCEPTED)

    interface, task_runner = build_interface([accepted], qtbot)
    try:
        interface._on_item_clicked(interface.list_widget.item(0))
        qtbot.waitUntil(lambda: accepted in interface.downloaded, timeout=5000)
    finally:
        task_runner.shutdown()

    assert accepted.status is SubtitleStatus.MANUALLY_DOWNLOADED
    assert download_environment == [accepted]


def test_auto_downloaded_subtitles_render_as_downloaded_without_redownload(qtbot, download_environment) -> None:
    auto_downloaded = make_subtitle("Auto.Sub", 96, SubtitleStatus.AUTO_DOWNLOADED)

    interface, task_runner = build_interface([auto_downloaded], qtbot)
    task_runner.shutdown()

    assert auto_downloaded in interface.downloaded
    assert download_environment == []


def test_action_row_overlays_buttons_and_keeps_item_text_when_manual_handling_enabled(
    qtbot, download_environment
) -> None:
    from qfluentwidgets import TransparentToolButton

    from subsearch.runtime.config import constants
    from subsearch.ui.cards.download_manager import SubtitleActionRow

    auto_downloaded = make_subtitle("Auto.Sub", 96, SubtitleStatus.AUTO_DOWNLOADED)

    interface, task_runner = build_interface([auto_downloaded], qtbot)
    interface._store.write("download_manager.manually_handle_post_processing", True)
    item = interface.list_widget.item(0)
    interface._attach_action_buttons(item, auto_downloaded)
    try:
        row = interface.list_widget.itemWidget(item)
        assert isinstance(row, SubtitleActionRow)
        buttons = row.findChildren(TransparentToolButton)
        assert len(buttons) == 2
        move_button, place_button = buttons
        assert "move all subtitles to" in move_button.toolTip().lower()
        assert place_button.isEnabled() == constants.VIDEO_FILE.file_exists
        # The item keeps its native icon and text so the row stays aligned with
        # every other row; the widget only adds the trailing action buttons.
        assert "Auto.Sub" in item.text()
    finally:
        task_runner.shutdown()


def test_populate_with_no_results_shows_skip_reasons(qtbot, download_environment) -> None:
    interface, task_runner = build_interface([], qtbot)
    try:
        interface.populate([], ["yifysubtitles skipped: needs an IMDb match and none was found for this search"])
    finally:
        task_runner.shutdown()

    placeholder_text = interface._empty_label.text()
    assert "No subtitles found" in placeholder_text
    assert "yifysubtitles skipped" in placeholder_text


def test_second_search_replaces_no_results_placeholder(qtbot, download_environment) -> None:
    interface, task_runner = build_interface([], qtbot)
    try:
        interface.populate([], ["subsource skipped: disabled in settings"])
        interface.reset_for_search()
        interface.populate([make_subtitle("Found.Sub", 95, SubtitleStatus.ACCEPTED)])
    finally:
        task_runner.shutdown()

    assert not hasattr(interface, "_empty_label")
    assert interface.list_widget.count() == 1


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
