import time

from PySide6.QtCore import QObject, QTimer, Signal

from subsearch.runtime.models.model import SearchOutcome, Subtitle, SubtitleStatus
from subsearch.ui.state.store import SettingsStore
from subsearch.ui.state.tasks import Worker

_SAMPLE_COUNT = 100
_PROVIDERS = ("subsource", "opensubtitles", "yifysubtitles")
_TITLES = (
    "The.Matrix.1999",
    "Inception.2010",
    "Interstellar.2014",
    "Blade.Runner.2049.2017",
    "Dune.Part.Two.2024",
    "Arrival.2016",
    "The.Dark.Knight.2008",
    "Mad.Max.Fury.Road.2015",
    "Parasite.2019",
    "Whiplash.2014",
)
_QUALITIES = (
    "1080p.BluRay.x264-GROUP",
    "720p.WEBRip-ANOTHER",
    "YIFY",
    "HDTV.XviD-OLD",
    "DVDRip-DUSTY",
    "2160p.WEB-DL.x265-HDR",
    "1080p.WEB.H264-CAKES",
)
_SIMULATED_SEARCH_SECONDS = 2


def _make_fixture_subtitles() -> list[Subtitle]:
    subtitles = []
    for index in range(_SAMPLE_COUNT):
        token_result = max(20, 99 - index)
        provider = _PROVIDERS[index % len(_PROVIDERS)]
        title = _TITLES[index % len(_TITLES)]
        quality = _QUALITIES[index % len(_QUALITIES)]
        subtitles.append(
            Subtitle(
                token_result=token_result,
                provider_name=provider,
                subtitle_name=f"{title}.{quality}",
                download_url="https://example.invalid/mock.zip",
                request_data={},
            )
        )
    return subtitles


class DevSearchWorker(Worker):
    def __init__(self, _imdb_id: str = "") -> None:
        super().__init__()

    def execute(self) -> SearchOutcome:
        time.sleep(_SIMULATED_SEARCH_SECONDS)
        return SearchOutcome(_make_fixture_subtitles(), ["yifysubtitles skipped: dev stub sample reason"])


class DevSubtitleDownloadService(QObject):
    started = Signal(object)
    succeeded = Signal(object)
    failed = Signal(object, str)

    _DOWNLOAD_DELAY_MS = 1200

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._queue: list[Subtitle] = []
        self._active: Subtitle | None = None
        self._download_number = 0

    def set_download_total(self, download_total: int) -> None:
        pass

    def enqueue(self, subtitle: Subtitle) -> None:
        if subtitle is self._active or subtitle in self._queue:
            return
        self._queue.append(subtitle)
        self._start_next()

    def _start_next(self) -> None:
        if self._active is not None or not self._queue:
            return
        subtitle = self._queue.pop(0)
        self._active = subtitle
        self.started.emit(subtitle)
        QTimer.singleShot(self._DOWNLOAD_DELAY_MS, lambda: self._resolve(subtitle))

    def _resolve(self, subtitle: Subtitle) -> None:
        self._download_number += 1
        self._active = None
        if self._download_number % 2 == 0:
            subtitle.status = SubtitleStatus.MANUALLY_DOWNLOADED
            self.succeeded.emit(subtitle)
        else:
            subtitle.status = SubtitleStatus.DOWNLOAD_FAILED
            self.failed.emit(subtitle, "dev stub: simulated failure")
        self._start_next()


class DevPostProcessingService(QObject):
    succeeded = Signal()
    failed = Signal(str)

    def unpack_and_move(self, store: SettingsStore) -> None:
        self.succeeded.emit()

    def unpack_rename_and_place(self, store: SettingsStore) -> None:
        self.succeeded.emit()
