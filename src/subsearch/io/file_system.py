import re
import shutil
import struct
import tempfile
import time
import traceback
import zipfile
from io import BufferedReader
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Iterable, Optional

if TYPE_CHECKING:
    import requests
    from curl_cffi.requests import Response as CurlResponse

from subsearch.io.file_tracker import get_file_tracker
from subsearch.parsing import release_parser
from subsearch.runtime.config import session as config_session
from subsearch.runtime.config.defaults import ConfigKey
from subsearch.runtime.logging.events import LogEvent
from subsearch.runtime.logging.logger import log
from subsearch.runtime.models import MatchTier, Subtitle, classify_match_tier


def create_path_from_string(
    string: str, path_resolution: str, file_directory: Path, create_missing_directory: bool = True
) -> Path:
    path = file_directory
    if path_resolution == "relative":
        if string == ".":
            path = file_directory
        elif string.startswith(".\\") and len(string) > 2:
            path = file_directory.joinpath(string[2:])
        elif string == "..":
            path = file_directory.parent
        elif string.startswith("..\\") and len(string) > 3:
            path = file_directory.parent.joinpath(string[3:])
    elif path_resolution == "absolute":
        path = Path(string)

    if not path.is_dir() and not create_missing_directory:
        log.event(LogEvent.FS_DESTINATION_MISSING, level="warning", path=path, fallback=file_directory)
        return file_directory

    path.mkdir(parents=True, exist_ok=True)
    return path


_ZIP_MAGIC_BYTES = (b"PK\x03\x04", b"PK\x05\x06", b"PK\x07\x08")


def is_zip_payload(chunk: bytes) -> bool:
    return chunk.startswith(_ZIP_MAGIC_BYTES)


_HASH_MATCH_PREFIX = "hashmatch__"


def _cloudflare_block_reason(response: "CurlResponse") -> str:
    headers = response.headers
    mitigated = headers.get("cf-mitigated")
    if mitigated:
        return str(mitigated)
    if "cloudflare" in headers.get("server", "").lower() and response.status_code == 403:
        return "blocked"
    return "none"


def download_subtitle(
    subtitle: Subtitle, index_position: int, index_size: int, tmp_dir: Path, extraction_dir: Path
) -> bool:
    from subsearch.io.http import get_session

    log.event(
        LogEvent.DOWNLOAD_SUBTITLE,
        provider=subtitle.provider_name,
        position=index_position,
        size=index_size,
        subtitle_name=subtitle.subtitle_name,
    )
    session = get_session()
    response = session.get(subtitle.download_url, headers=subtitle.download_headers, stream=True)
    chunks = response.iter_content(chunk_size=1024)
    first_chunk = next(chunks, b"")
    if is_zip_payload(first_chunk):
        _save_zip_archive(subtitle, tmp_dir, first_chunk, chunks)
        return True
    raw_extension = _raw_subtitle_extension(response)
    if raw_extension is not None:
        _save_raw_subtitle(subtitle, extraction_dir, raw_extension, first_chunk, chunks)
        return True
    log.event(
        LogEvent.DOWNLOAD_NOT_ZIP,
        level="warning",
        provider=subtitle.provider_name,
        subtitle_name=subtitle.subtitle_name,
        status_code=response.status_code,
        cloudflare=_cloudflare_block_reason(response),
        url=subtitle.download_url,
    )
    return False


def _save_zip_archive(subtitle: Subtitle, tmp_dir: Path, first_chunk: bytes, chunks: Iterable[bytes]) -> None:
    name_prefix = _HASH_MATCH_PREFIX if subtitle.hash_match else ""
    tmp_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        dir=tmp_dir, prefix=f"{name_prefix}{subtitle.subtitle_id}_", suffix=".zip", delete=False
    ) as fd:
        download_path = Path(fd.name)
        get_file_tracker().track(download_path)
        fd.write(first_chunk)
        for chunk in chunks:
            fd.write(chunk)


def _save_raw_subtitle(
    subtitle: Subtitle, extraction_dir: Path, extension: str, first_chunk: bytes, chunks: Iterable[bytes]
) -> None:
    extraction_dir.mkdir(parents=True, exist_ok=True)
    name_prefix = _HASH_MATCH_PREFIX if subtitle.hash_match else ""
    stem = f"{name_prefix}{subtitle.subtitle_name}"
    download_path = _next_available_path(extraction_dir, stem, extension)
    get_file_tracker().track(download_path)
    with download_path.open("wb") as fd:
        fd.write(first_chunk)
        for chunk in chunks:
            fd.write(chunk)


_SUBTITLE_EXTENSIONS = {".srt", ".sub", ".ass", ".ssa", ".vtt"}
_MAX_UNCOMPRESSED_BYTES = 50 * 1024 * 1024  # 50 MB , generous for any subtitle archive

_CONTENT_TYPE_EXTENSIONS = {
    "text/srt": ".srt",
    "application/x-subrip": ".srt",
    "text/vtt": ".vtt",
    "text/x-ssa": ".ass",
}

# matches a content-disposition filename, e.g. filename=Show.S01E01.en.srt or filename*=UTF-8''Show.srt
_CONTENT_DISPOSITION_FILENAME_PATTERN = re.compile(r"filename\*?=(?:UTF-8\'\')?\"?([^\";]+)\"?", re.IGNORECASE)


def _content_disposition_filename(response: "CurlResponse") -> str | None:
    disposition = response.headers.get("content-disposition", "")
    match = _CONTENT_DISPOSITION_FILENAME_PATTERN.search(disposition)
    return match.group(1).strip() if match else None


def _raw_subtitle_extension(response: "CurlResponse") -> str | None:
    filename = _content_disposition_filename(response)
    if filename:
        suffix = Path(filename).suffix.lower()
        if suffix in _SUBTITLE_EXTENSIONS:
            return suffix
    content_type = response.headers.get("content-type", "").split(";")[0].strip().lower()
    return _CONTENT_TYPE_EXTENSIONS.get(content_type)


def _archive_listing(archive: zipfile.ZipFile) -> str:
    return "\n".join(f"  {info.filename} ({info.file_size} bytes)" for info in archive.infolist())


def _safe_extract_archive(archive: zipfile.ZipFile, dst: Path, hash_match: bool = False) -> int:
    members = archive.infolist()
    total_uncompressed = sum(info.file_size for info in members)
    log.event(
        LogEvent.FS_ARCHIVE_CONTENTS,
        level="debug",
        name=archive.filename or "archive",
        member_count=len(members),
        size=total_uncompressed,
        listing=_archive_listing(archive),
    )
    if total_uncompressed > _MAX_UNCOMPRESSED_BYTES:
        log.event(LogEvent.FS_ARCHIVE_OVERSIZE, level="warning", size=total_uncompressed)
        return 0

    extracted_count = 0
    dst_resolved = dst.resolve()
    for member in members:
        member_path = (dst / member.filename).resolve()
        if not str(member_path).startswith(str(dst_resolved)):
            log.event(LogEvent.FS_ARCHIVE_UNSAFE_PATH, level="warning", filename=member.filename)
            continue
        if member_path.suffix.lower() not in _SUBTITLE_EXTENSIONS:
            log.event(
                LogEvent.FS_ARCHIVE_MEMBER_IGNORED,
                level="debug",
                filename=member.filename,
                reason="not a subtitle file",
            )
            continue
        extracted_path = Path(archive.extract(member, dst))
        if hash_match and not extracted_path.name.startswith(_HASH_MATCH_PREFIX):
            renamed_path = extracted_path.with_name(f"{_HASH_MATCH_PREFIX}{extracted_path.name}")
            extracted_path.rename(renamed_path)
            extracted_path = renamed_path
        get_file_tracker().track(extracted_path)
        extracted_count += 1
    return extracted_count


def _extract_archive_file(file: Path, dst: Path) -> int:
    log.event(LogEvent.EXTRACT, src=file, dst=dst)
    try:
        with zipfile.ZipFile(file) as archive:
            return _safe_extract_archive(archive, dst, hash_match=file.name.startswith(_HASH_MATCH_PREFIX))
    except zipfile.BadZipFile, OSError:
        log.event(LogEvent.FS_ARCHIVE_UNREADABLE, level="error", name=file.name, traceback=traceback.format_exc())
        return 0


def extract_files_in_dir(src: Path, dst: Path, extension: str = ".zip") -> int:
    extracted_count = 0
    for file in src.glob(f"*{extension}"):
        extracted_count += _extract_archive_file(file, dst)
    return extracted_count


def extract_subtitle_by_id(subtitle_id: str, src: Path, dst: Path, extension: str = ".zip") -> int:
    dst.mkdir(parents=True, exist_ok=True)
    extracted_count = 0
    for file in src.glob(f"*{subtitle_id}*{extension}"):
        extracted_count += _extract_archive_file(file, dst)
    return extracted_count


def _subtitle_files_in(directory: Path) -> list[Path]:
    if not directory.is_dir():
        return []
    return sorted(
        file for file in directory.iterdir() if file.is_file() and file.suffix.lower() in _SUBTITLE_EXTENSIONS
    )


def count_subtitle_files(directory: Path) -> int:
    return len(_subtitle_files_in(directory))


def count_raw_subtitles_by_name(subtitle_name: str, directory: Path) -> int:
    if not directory.is_dir():
        return 0
    return sum(
        1
        for file in directory.iterdir()
        if file.is_file() and file.suffix.lower() in _SUBTITLE_EXTENSIONS and file.stem.startswith(subtitle_name)
    )


def find_best_subtitle_match(release_name: str, subs_dir: Path) -> Path:
    config = config_session.get_config_session()
    weights = config.read(ConfigKey.SEARCH_TOKEN_WEIGHTS)
    multipliers = config.read(ConfigKey.SEARCH_TOKEN_MULTIPLIERS)
    accept_threshold = config.read(ConfigKey.SEARCH_ACCEPT_THRESHOLD)
    best_rank = (MatchTier.C, 0)
    best_match = Path(".")
    for file in _subtitle_files_in(subs_dir):
        is_hash_match = file.name.startswith(_HASH_MATCH_PREFIX)
        token_name = file.name.removeprefix(_HASH_MATCH_PREFIX)
        token_score = release_parser.score_subtitle_tokens(token_name, release_name, weights, multipliers)
        tier = classify_match_tier(is_hash_match, token_score, accept_threshold)
        rank = (tier, token_score)
        if rank > best_rank:
            best_rank = rank
            best_match = file
    return best_match


def _next_available_path(directory: Path, stem: str, extension: str) -> Path:
    candidate = directory / f"{stem}{extension}"
    version = 1
    while candidate.exists():
        candidate = directory / f"{stem}_v{version}{extension}"
        version += 1
    return candidate


def rename_subtitle_to_release(file_path: Path, release_name: str, extension: str = ".srt") -> Path:
    new_file_path = _next_available_path(file_path.parent, release_name, extension)
    log.event(LogEvent.RENAME, src=file_path, dst=new_file_path)
    file_path.rename(new_file_path)
    return new_file_path


def autoload_rename(release_name: str, subs_dir: Path) -> Path:
    matched_file = find_best_subtitle_match(release_name, subs_dir)
    return rename_subtitle_to_release(matched_file, release_name, matched_file.suffix)


def move_all(src: Path, dst: Path) -> int:
    if src.resolve() == dst.resolve():
        return 0
    moved_count = 0
    for file in _subtitle_files_in(src):
        destination = _next_available_path(dst, file.stem, file.suffix)
        log.event(LogEvent.MOVE, src=file, dst=destination)
        file.absolute().replace(destination)
        moved_count += 1
    return moved_count


def move_and_replace(source_file: Path, destination_directory: Path) -> None:
    source_file.replace(destination_directory / source_file.name)
    log.event(LogEvent.MOVE, src=source_file, dst=destination_directory)


def del_file_type(cwd: Path, extension: str) -> None:
    for file in Path(cwd).glob(f"*{extension}"):
        log.event(LogEvent.REMOVE, src=file)
        file.unlink()


def del_directory(directory: Path) -> None:
    log.event(LogEvent.REMOVE, src=directory)
    shutil.rmtree(directory)


def directory_is_empty(directory: Path) -> bool:
    if not any(directory.iterdir()):
        return True
    return False


def del_directory_content(directory: Path) -> None:
    for item in directory.iterdir():
        log.event(LogEvent.REMOVE, src=item)
        if item.is_file():
            item.unlink()
        elif item.is_dir():
            shutil.rmtree(item)


def create_directory(path: Path) -> bool:
    if path.exists():
        return False
    log.event(LogEvent.FS_CREATING, level="debug", path=path)
    path.mkdir(parents=True, exist_ok=True)
    return True


def get_file_hash(file_path: Path) -> str:
    log.event(LogEvent.FS_HASHING, level="debug")
    if not file_path.exists():
        return ""

    hash_algorithm = MPCHashAlgorithm(file_path)
    return hash_algorithm.get_hash()


def count_files_in_directory(path: Path, extensions: Optional[Iterable[str]] = None) -> int:
    extensions = {ext.lower() for ext in extensions} if extensions else None
    file_count = sum(
        1 for file in path.iterdir() if file.is_file() and (extensions is None or file.suffix.lower() in extensions)
    )
    return file_count


class MPCHashAlgorithm:
    def __init__(self, file_path: Path, **kwargs: Any) -> None:
        file_size = file_path.stat().st_size
        self.file_path = file_path
        self.chunk_size = kwargs.get("chunk_size", 65536)
        self.file_size, self.hash_chunk = file_size, file_size
        self.hash = self.mpc_hash_algorithm()

    def mpc_hash_algorithm(self) -> str:
        if not self.valid_file_size():
            return ""

        with open(self.file_path, "rb") as file:
            self.byte_size = struct.calcsize("<q")
            self.update_hash_chunk(file)
            file.seek(max(0, self.file_size - self.chunk_size), 0)
            self.update_hash_chunk(file)
        return "%016x" % self.hash_chunk

    def valid_file_size(self) -> bool:
        if self.file_size < self.chunk_size * 2:
            log.event(LogEvent.FS_INVALID_FILE_SIZE, level="warning", size=self.file_size)
            return False
        return True

    def update_hash_chunk(self, file: BufferedReader) -> None:
        for _ in range(self.chunk_size // self.byte_size):
            buffer = file.read(self.byte_size)
            (chunk_value,) = struct.unpack("<q", buffer)
            self.hash_chunk += chunk_value
            self.hash_chunk = self.hash_chunk & 0xFFFFFFFFFFFFFFFF

    def get_hash(self) -> str:
        return self.hash


def download_response(
    msi_package_path: Path,
    response: "requests.Response | CurlResponse",
    on_progress: Callable[[float], None] | None = None,
) -> None:
    start_time = time.time()
    with open(msi_package_path, "wb") as msi_file:
        total_size = int(response.headers.get("content-length", 0))
        downloaded_size = 0
        log.event(LogEvent.DOWNLOAD_STARTED, filename=msi_package_path.name)
        log.event(LogEvent.DOWNLOAD_PROGRESS, percentage="0.00")
        for chunk in response.iter_content(chunk_size=128):
            msi_file.write(chunk)
            downloaded_size += len(chunk)
            if total_size > 0:
                progress_percentage = (downloaded_size / total_size) * 100
                if on_progress is not None:
                    on_progress(progress_percentage)
                elapsed_time = time.time() - start_time
                if elapsed_time >= 0.5:
                    log.event(LogEvent.DOWNLOAD_PROGRESS, percentage=f"{progress_percentage:.2f}")
                    start_time = time.time()
        if on_progress is not None:
            on_progress(100.0)
        log.event(LogEvent.DOWNLOAD_COMPLETED)
