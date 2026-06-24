from pathlib import Path

from PySide6.QtCore import QObject

from subsearch.runtime.config import SEARCH_RESOLVER, SEARCH_SUBJECT, WORKSPACE
from subsearch.runtime.recorder import LogLevel, capture


class VideoFileService(QObject):
    def rename_active_video(self, filename: str) -> None:
        subject, workspace = SEARCH_RESOLVER.re_resolve(filename, WORKSPACE.file_directory)
        SEARCH_SUBJECT.copy_from(subject)
        WORKSPACE.copy_from(workspace)
        capture(f"Search term set: {filename}")
        capture(repr(SEARCH_SUBJECT), level=LogLevel.DEBUG)
        capture(repr(WORKSPACE), level=LogLevel.DEBUG)

    def select_video(self, file_path: Path) -> None:
        subject, workspace = SEARCH_RESOLVER.re_resolve(file_path.name, file_path.parent)
        SEARCH_SUBJECT.copy_from(subject)
        WORKSPACE.copy_from(workspace)
        capture(f"Selected {SEARCH_SUBJECT.search_term + SEARCH_SUBJECT.file_extension}")
        capture(repr(SEARCH_SUBJECT), level=LogLevel.DEBUG)
        capture(repr(WORKSPACE), level=LogLevel.DEBUG)
