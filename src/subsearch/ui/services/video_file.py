from pathlib import Path

from PySide6.QtCore import QObject

from subsearch.runtime.config import SEARCH_RESOLVER, SEARCH_SUBJECT, WORKSPACE
from subsearch.runtime.logging.events import LogEvent
from subsearch.runtime.logging.logger import log


class VideoFileService(QObject):
    def rename_active_video(self, filename: str) -> None:
        subject, workspace = SEARCH_RESOLVER.re_resolve(filename, WORKSPACE.file_directory)
        SEARCH_SUBJECT.copy_from(subject)
        WORKSPACE.copy_from(workspace)
        log.event(LogEvent.SEARCH_TERM_SET, term=filename)
        log.dataclass(SEARCH_SUBJECT)
        log.dataclass(WORKSPACE)

    def select_video(self, file_path: Path) -> None:
        subject, workspace = SEARCH_RESOLVER.re_resolve(file_path.name, file_path.parent)
        SEARCH_SUBJECT.copy_from(subject)
        WORKSPACE.copy_from(workspace)
        log.event(LogEvent.VIDEO_FILE_SELECTED, filename=SEARCH_SUBJECT.search_term + SEARCH_SUBJECT.file_extension)
        log.dataclass(SEARCH_SUBJECT)
        log.dataclass(WORKSPACE)
