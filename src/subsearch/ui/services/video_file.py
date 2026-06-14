from pathlib import Path

from PySide6.QtCore import QObject

from subsearch.runtime.config import VIDEO_FILE, VIDEO_FILE_RESOLVER
from subsearch.runtime.logging.logger import log


class VideoFileService(QObject):
    def rename_active_video(self, filename: str) -> None:
        resolved = VIDEO_FILE_RESOLVER.re_resolve(filename, VIDEO_FILE.file_directory)
        VIDEO_FILE.copy_from(resolved)
        log.event("search_term_set", term=filename)
        log.dataclass(VIDEO_FILE, to_console=False)

    def select_video(self, file_path: Path) -> None:
        resolved = VIDEO_FILE_RESOLVER.re_resolve(file_path.name, file_path.parent)
        VIDEO_FILE.copy_from(resolved)
        log.event("video_file_selected", filename=VIDEO_FILE.filename + VIDEO_FILE.file_extension)
        log.dataclass(VIDEO_FILE, to_console=False)
