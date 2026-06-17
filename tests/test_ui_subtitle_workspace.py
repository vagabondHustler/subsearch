import pytest

from subsearch.runtime.models import Subtitle, SubtitleStatus


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
    from subsearch.runtime.config import composition

    downloaded = []

    def fake_download(subtitle, number, total, tmp_dir, extraction_dir):
        downloaded.append(subtitle)
        return True

    monkeypatch.setattr(file_system, "download_subtitle", fake_download)
    monkeypatch.setattr(composition.WORKSPACE, "download_directory", tmp_path / "tmp", raising=False)
    monkeypatch.setattr(composition.WORKSPACE, "extraction_directory", tmp_path / "tmp", raising=False)
    (tmp_path / "tmp").mkdir()
    return downloaded


def build_interface(subtitles, qtbot):
    from subsearch.ui.cards.subtitle_workspace import ManualSearchInterface
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

    assert accepted.status is SubtitleStatus.MANUAL_DOWNLOAD
    assert download_environment == [accepted]


def test_auto_downloaded_subtitles_render_as_downloaded_without_redownload(qtbot, download_environment) -> None:
    auto_downloaded = make_subtitle("Auto.Sub", 96, SubtitleStatus.AUTO_DOWNLOAD)

    interface, task_runner = build_interface([auto_downloaded], qtbot)
    task_runner.shutdown()

    assert auto_downloaded in interface.downloaded
    assert download_environment == []


def test_action_row_overlays_buttons_and_keeps_item_text_when_manual_post_processing_enabled(
    qtbot, download_environment
) -> None:
    from qfluentwidgets import TransparentToolButton

    from subsearch.runtime.config import composition
    from subsearch.ui.cards.subtitle_workspace import SubtitleActionRow

    auto_downloaded = make_subtitle("Auto.Sub", 96, SubtitleStatus.AUTO_DOWNLOAD)

    interface, task_runner = build_interface([auto_downloaded], qtbot)
    interface._store.write("subtitle_workspace.manual_post_processing", True)
    item = interface.list_widget.item(0)
    interface._attach_action_buttons(item, auto_downloaded)
    try:
        row = interface.list_widget.itemWidget(item)
        assert isinstance(row, SubtitleActionRow)
        buttons = row.findChildren(TransparentToolButton)
        assert len(buttons) == 3
        move_button, place_button, open_location_button = buttons
        assert "move this subtitle to" in move_button.toolTip().lower()
        assert place_button.isEnabled() == composition.SEARCH_SUBJECT.file_exists
        # The open-location button stays disabled until a subtitle is delivered.
        assert "open the folder" in open_location_button.toolTip().lower()
        assert not open_location_button.isEnabled()
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


class _FakeDropEvent:
    def __init__(self, *paths):
        from PySide6.QtCore import QMimeData, QUrl

        self.mime_data = QMimeData()
        self.mime_data.setUrls([QUrl.fromLocalFile(str(path)) for path in paths])
        self.accepted = False
        self.ignored = False

    def mimeData(self):
        return self.mime_data

    def acceptProposedAction(self) -> None:
        self.accepted = True

    def ignore(self) -> None:
        self.ignored = True


def test_dropping_video_file_selects_it_and_requests_search(qtbot, tmp_path) -> None:
    interface, task_runner = build_interface([], qtbot)
    selected = []
    requests = []
    interface._search_bar._video_file_service.select_video = lambda path: selected.append(path)
    interface.research_requested.connect(lambda imdb_id: requests.append(imdb_id))
    video_file = tmp_path / "Shrek.2001.1080p.BluRay.x264-YOLO.mkv"
    video_file.touch()
    event = _FakeDropEvent(video_file)
    try:
        interface.dropEvent(event)
    finally:
        task_runner.shutdown()

    assert event.accepted
    assert selected == [video_file]
    assert requests == [""]


def test_dropping_unsupported_file_is_ignored(qtbot, tmp_path) -> None:
    interface, task_runner = build_interface([], qtbot)
    requests = []
    interface.research_requested.connect(lambda imdb_id: requests.append(imdb_id))
    text_file = tmp_path / "notes.txt"
    text_file.touch()
    event = _FakeDropEvent(text_file)
    try:
        interface.dropEvent(event)
    finally:
        task_runner.shutdown()

    assert event.ignored
    assert requests == []


def test_dropping_multiple_files_is_ignored(qtbot, tmp_path) -> None:
    interface, task_runner = build_interface([], qtbot)
    requests = []
    interface.research_requested.connect(lambda imdb_id: requests.append(imdb_id))
    first = tmp_path / "First.mkv"
    second = tmp_path / "Second.mkv"
    first.touch()
    second.touch()
    event = _FakeDropEvent(first, second)
    try:
        interface.dropEvent(event)
    finally:
        task_runner.shutdown()

    assert event.ignored
    assert requests == []


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
