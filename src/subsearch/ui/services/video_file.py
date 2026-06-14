from pathlib import Path

from PySide6.QtCore import QObject

from subsearch.runtime.config import SEARCH_RESOLVER, SEARCH_SUBJECT, WORKSPACE
from subsearch.runtime.logging.logger import log


class VideoFileService(QObject):
    def rename_active_video(self, filename: str) -> None:
        subject, workspace = SEARCH_RESOLVER.re_resolve(filename, WORKSPACE.file_directory)
        SEARCH_SUBJECT.copy_from(subject)
        WORKSPACE.copy_from(workspace)
        log.event("search_term_set", term=filename)
        log.dataclass(SEARCH_SUBJECT, to_console=False)
        log.dataclass(WORKSPACE, to_console=False)

    def select_video(self, file_path: Path) -> None:
        subject, workspace = SEARCH_RESOLVER.re_resolve(file_path.name, file_path.parent)
        SEARCH_SUBJECT.copy_from(subject)
        WORKSPACE.copy_from(workspace)
        log.event("video_file_selected", filename=SEARCH_SUBJECT.search_term + SEARCH_SUBJECT.file_extension)
        log.dataclass(SEARCH_SUBJECT, to_console=False)
        log.dataclass(WORKSPACE, to_console=False)
