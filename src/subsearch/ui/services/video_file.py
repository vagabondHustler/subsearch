from pathlib import Path

from PySide6.QtCore import QObject

from subsearch.runtime.config.constants import VIDEO_FILE, VIDEO_FILE_RESOLVER


class VideoFileService(QObject):
    def rename_active_video(self, filename: str) -> None:
        resolved = VIDEO_FILE_RESOLVER.re_resolve(filename, VIDEO_FILE.file_directory)
        VIDEO_FILE.copy_from(resolved)

    def select_video(self, file_path: Path) -> None:
        resolved = VIDEO_FILE_RESOLVER.re_resolve(file_path.name, file_path.parent)
        VIDEO_FILE.copy_from(resolved)
