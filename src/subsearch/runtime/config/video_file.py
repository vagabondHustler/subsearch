import sys
from pathlib import Path

from subsearch.runtime.config.defaults import SUPPORTED_FILE_EXTENSIONS
from subsearch.runtime.models import VideoFile


class VideoFileResolver:
    def __init__(self, supported_extensions: list[str]) -> None:
        self._supported_extensions = supported_extensions

    def resolve_from_argv(self) -> VideoFile:
        for argument in sys.argv:
            file_path = self._find_video_file_path(argument)
            if file_path is not None:
                return self._build_from_path(file_path)
        return self._build_empty()

    def re_resolve(self, filename: str, file_directory: Path) -> VideoFile:
        suffix = Path(filename).suffix
        has_video_extension = suffix.lstrip(".") in self._supported_extensions
        file_path = file_directory / filename
        if has_video_extension and file_path.exists():
            return self._build_from_path(file_path)
        # Without a real video file these are provisional; Bootstrap._anchor_working_directory
        # is the authority for the no-file case and overwrites all three from config.
        return VideoFile(
            file_exists=False,
            filename=Path(filename).stem if has_video_extension else filename,
            file_hash="",
            file_extension=suffix if has_video_extension else "",
            file_path=file_path,
            file_directory=file_directory,
            extraction_directory=file_directory,
            download_directory=file_directory,
        )

    def _find_video_file_path(self, argument: str) -> Path | None:
        argument_path = Path(argument)
        extension = argument_path.suffix.lstrip(".")
        if extension in self._supported_extensions and "\\" in argument:
            return argument_path
        return None

    def _build_from_path(self, file_path: Path) -> VideoFile:
        return VideoFile(
            file_exists=True,
            filename=file_path.stem,
            file_hash="",
            file_extension=file_path.suffix,
            file_path=file_path,
            file_directory=file_path.parent,
            extraction_directory=file_path.parent / "subs",
            download_directory=file_path.parent / "tmp_subsearch",
        )

    def _build_empty(self) -> VideoFile:
        return VideoFile(
            file_exists=False,
            filename="",
            file_hash="",
            file_extension="",
            file_path=Path(""),
            file_directory=Path(""),
            extraction_directory=Path(""),
            download_directory=Path(""),
        )


def get_video_file_data() -> VideoFile:
    return VideoFileResolver(SUPPORTED_FILE_EXTENSIONS).resolve_from_argv()
