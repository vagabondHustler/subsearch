from pathlib import Path

from PySide6.QtCore import QObject

from subsearch.runtime.config import VIDEO_FILE, VIDEO_FILE_RESOLVER
from subsearch.runtime.logging.logger import log


class VideoFileService(QObject):
    def rename_active_video(self, filename: str) -> None:
        resolved = VIDEO_FILE_RESOLVER.re_resolve(filename, VIDEO_FILE.file_directory)
        VIDEO_FILE.copy_from(resolved)
        self._log_active_video()

    def select_video(self, file_path: Path) -> None:
        resolved = VIDEO_FILE_RESOLVER.re_resolve(file_path.name, file_path.parent)
        VIDEO_FILE.copy_from(resolved)
        self._log_active_video()

    def _log_active_video(self) -> None:
        log.event("video_file_selected", filename=VIDEO_FILE.filename + VIDEO_FILE.file_extension)
        log.dataclass(VIDEO_FILE, to_console=False)
