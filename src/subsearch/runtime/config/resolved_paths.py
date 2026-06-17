from dataclasses import dataclass
from pathlib import Path

from subsearch.runtime.models import AppConfig


@dataclass(slots=True, frozen=True)
class ResolvedDirectories:
    download_directory: Path
    extraction_directory: Path


class PathResolver:
    """Single source of truth for translating the stored path sentinels into real paths.

    The config keeps sentinels on purpose: an empty download/extraction directory means
    "use the default", and the relative video_file_directory ("." by default) follows
    whichever directory the searched video file lives in. Everything that needs a real
    path resolves it here instead of re-deriving the sentinel meaning at every call site.
    """

    def __init__(self, tmp_directory: Path, default_extraction_directory: Path) -> None:
        self._tmp_directory = tmp_directory
        self._default_extraction_directory = default_extraction_directory

    def default_download_directory(self) -> Path:
        return self._tmp_directory

    def default_extraction_directory(self) -> Path:
        return self._default_extraction_directory

    def resolve_directories(self, app_config: AppConfig) -> ResolvedDirectories:
        paths = app_config.paths
        download = paths["download_directory"].strip()
        extraction = paths["extraction_directory"].strip()
        return ResolvedDirectories(
            download_directory=Path(download) if download else self._tmp_directory,
            extraction_directory=Path(extraction) if extraction else self._default_extraction_directory,
        )

    def resolve_post_processing_target(self, app_config: AppConfig, file_directory: Path) -> Path:
        from subsearch.io import file_system

        paths = app_config.paths
        return file_system.create_path_from_string(
            paths["video_file_directory"],
            paths["path_resolution"],
            file_directory,
            paths["create_missing_directory"],
        )
