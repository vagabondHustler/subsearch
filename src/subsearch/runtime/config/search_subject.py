import sys
from pathlib import Path

from subsearch.runtime.config.defaults import SUPPORTED_FILE_EXTENSIONS
from subsearch.runtime.models import SearchSubject, Workspace


class SearchResolver:
    def __init__(self, supported_extensions: list[str]) -> None:
        self._supported_extensions = supported_extensions

    def resolve_from_argv(self) -> tuple[SearchSubject, Workspace]:
        for argument in sys.argv:
            file_path = self._find_video_file_path(argument)
            if file_path is not None:
                return self._build_from_path(file_path)
        return self._build_empty()

    def re_resolve(self, search_term: str, file_directory: Path) -> tuple[SearchSubject, Workspace]:
        suffix = Path(search_term).suffix
        has_video_extension = suffix.lstrip(".") in self._supported_extensions
        file_path = file_directory / search_term
        if has_video_extension and file_path.exists():
            return self._build_from_path(file_path)
        subject = SearchSubject(
            file_exists=False,
            search_term=Path(search_term).stem if has_video_extension else search_term,
            file_hash="",
            file_extension=suffix if has_video_extension else "",
            file_path=None,
        )
        # Without a real video file these are provisional; Bootstrap._anchor_working_directory
        # is the authority for the no-file case and overwrites all three from config.
        workspace = Workspace(
            file_directory=file_directory,
            extraction_directory=file_directory,
            download_directory=file_directory,
        )
        return subject, workspace

    def _find_video_file_path(self, argument: str) -> Path | None:
        argument_path = Path(argument)
        extension = argument_path.suffix.lstrip(".")
        if extension in self._supported_extensions and "\\" in argument:
            return argument_path
        return None

    def _build_from_path(self, file_path: Path) -> tuple[SearchSubject, Workspace]:
        subject = SearchSubject(
            file_exists=True,
            search_term=file_path.stem,
            file_hash="",
            file_extension=file_path.suffix,
            file_path=file_path,
        )
        workspace = Workspace(
            file_directory=file_path.parent,
            extraction_directory=file_path.parent / "subs",
            download_directory=file_path.parent / "tmp_subsearch",
        )
        return subject, workspace

    def _build_empty(self) -> tuple[SearchSubject, Workspace]:
        subject = SearchSubject(
            file_exists=False,
            search_term="",
            file_hash="",
            file_extension="",
            file_path=None,
        )
        workspace = Workspace(
            file_directory=Path(""),
            extraction_directory=Path(""),
            download_directory=Path(""),
        )
        return subject, workspace


def get_search_data() -> tuple[SearchSubject, Workspace]:
    return SearchResolver(SUPPORTED_FILE_EXTENSIONS).resolve_from_argv()
