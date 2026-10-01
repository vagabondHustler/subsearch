import hashlib
import json
import re
import shutil
import struct
import tempfile
import time
import traceback
import zipfile
from io import BufferedReader
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Collection, Iterable, Optional

if TYPE_CHECKING:
    from curl_cffi.requests import Response as CurlResponse

from subsearch.runtime.models import Subtitle
from subsearch.runtime.recorder import LogLevel, capture


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
        capture(
            f"Destination directory {path} does not exist, moving to {file_directory} instead",
            level=LogLevel.WARNING,
        )
        return file_directory

    path.mkdir(parents=True, exist_ok=True)
    return path


_ZIP_MAGIC_BYTES = (b"PK\x03\x04", b"PK\x05\x06", b"PK\x07\x08")


def is_zip_payload(chunk: bytes) -> bool:
    return chunk.startswith(_ZIP_MAGIC_BYTES)


_HASH_MATCH_PREFIX = "hashmatch__"

# marks a subtitle that was already placed next to the video and later displaced, so it is not re-selected
_TESTED_MARKER = "_tested"


def _cloudflare_block_reason(response: "CurlResponse") -> str:
    headers = response.headers
    mitigated = headers.get("cf-mitigated")
    if mitigated:
        return str(mitigated)
    if "cloudflare" in headers.get("server", "").lower() and response.status_code == 403:
        return "blocked"
    return "none"


class DownloadedSubtitle:
    def __init__(self, path: Path, content_hash: str) -> None:
        self.path = path
        self.content_hash = content_hash


def download_subtitle(
    subtitle: Subtitle, index_position: int, index_size: int, tmp_dir: Path
) -> DownloadedSubtitle | None:
    from subsearch.io.http import get_session

    capture(f"Downloading {subtitle.subtitle_name}")
    session = get_session()
    response = session.get(subtitle.download_url, headers=subtitle.download_headers, stream=True)
    chunks = response.iter_content(chunk_size=1024)
    first_chunk = next(chunks, b"")
    if is_zip_payload(first_chunk):
        return _save_zip_archive(subtitle, tmp_dir, first_chunk, chunks)
    raw_extension = _raw_subtitle_extension(response)
    if raw_extension is not None:
        return _save_raw_subtitle(subtitle, tmp_dir, raw_extension, first_chunk, chunks)
    capture(
        f"{subtitle.provider_name}: {subtitle.subtitle_name} is not a zip "
        f"(status {response.status_code}, cloudflare {_cloudflare_block_reason(response)}) "
        f"from {subtitle.download_url}, skipping download",
        level=LogLevel.WARNING,
    )
    return None


def _write_chunks(file_descriptor: Any, first_chunk: bytes, chunks: Iterable[bytes]) -> str:
    digest = hashlib.sha256()
    file_descriptor.write(first_chunk)
    digest.update(first_chunk)
    for chunk in chunks:
        file_descriptor.write(chunk)
        digest.update(chunk)
    return digest.hexdigest()


def _save_zip_archive(
    subtitle: Subtitle, tmp_dir: Path, first_chunk: bytes, chunks: Iterable[bytes]
) -> DownloadedSubtitle:
    name_prefix = _HASH_MATCH_PREFIX if subtitle.hash_match else ""
    tmp_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        dir=tmp_dir, prefix=f"{name_prefix}{subtitle.subtitle_id}_", suffix=".zip", delete=False
    ) as fd:
        download_path = Path(fd.name)
        file_hash = _write_chunks(fd, first_chunk, chunks)
    return DownloadedSubtitle(download_path, file_hash)


def _save_raw_subtitle(
    subtitle: Subtitle, download_dir: Path, extension: str, first_chunk: bytes, chunks: Iterable[bytes]
) -> DownloadedSubtitle:
    download_dir.mkdir(parents=True, exist_ok=True)
    name_prefix = _HASH_MATCH_PREFIX if subtitle.hash_match else ""
    stem = f"{name_prefix}{subtitle.subtitle_name}"
    download_path = _next_available_path(download_dir, stem, extension)
    with download_path.open("wb") as fd:
        file_hash = _write_chunks(fd, first_chunk, chunks)
    return DownloadedSubtitle(download_path, file_hash)


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


def content_hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_content_hash(path: Path) -> str:
    return content_hash(path.read_bytes())


def _resolve_extraction_target(destination: Path, filename: str, payload: bytes) -> Path | None:
    target = destination / Path(filename).name
    if not target.exists():
        return target
    if file_content_hash(target) == content_hash(payload):
        capture(f"Skipping {target.name} (identical copy already extracted)", level=LogLevel.DEBUG)
        return None
    return _next_available_path(destination, target.stem, target.suffix)


def _safe_extract_archive(archive: zipfile.ZipFile, dst: Path, hash_match: bool = False) -> int:
    members = archive.infolist()
    total_uncompressed = sum(info.file_size for info in members)
    capture(
        f"Archive {archive.filename or 'archive'}: {len(members)} entries, "
        f"{total_uncompressed} bytes uncompressed\n{_archive_listing(archive)}",
        level=LogLevel.DEBUG,
    )
    if total_uncompressed > _MAX_UNCOMPRESSED_BYTES:
        capture(f"Archive uncompressed size {total_uncompressed} exceeds limit, skipping", level=LogLevel.WARNING)
        return 0

    extracted_count = 0
    dst_resolved = dst.resolve()
    for member in members:
        member_path = (dst / member.filename).resolve()
        if not str(member_path).startswith(str(dst_resolved)):
            capture(f"Skipping unsafe path in archive: {member.filename}", level=LogLevel.WARNING)
            continue
        if member_path.suffix.lower() not in _SUBTITLE_EXTENSIONS:
            capture(f"Ignoring {member.filename} (not a subtitle file)", level=LogLevel.DEBUG)
            continue
        payload = archive.read(member)
        member_name = Path(member.filename).name
        if hash_match and not member_name.startswith(_HASH_MATCH_PREFIX):
            member_name = f"{_HASH_MATCH_PREFIX}{member_name}"
        target = _resolve_extraction_target(dst, member_name, payload)
        if target is None:
            continue
        target.write_bytes(payload)
        extracted_count += 1
    return extracted_count


def _extract_archive_file(file: Path, dst: Path) -> int:
    capture(f"Extracting {file.name}")
    try:
        with zipfile.ZipFile(file) as archive:
            return _safe_extract_archive(archive, dst, hash_match=file.name.startswith(_HASH_MATCH_PREFIX))
    except zipfile.BadZipFile, OSError:
        capture(f"Skipping unreadable archive {file.name}\n{traceback.format_exc()}", level=LogLevel.ERROR)
        return 0


def extract_files_in_dir(
    src: Path, dst: Path, extension: str = ".zip", exclude_ids: Collection[str] = frozenset()
) -> int:
    extracted_count = 0
    for file in src.glob(f"*{extension}"):
        if any(f"{excluded_id}_" in file.stem for excluded_id in exclude_ids):
            continue
        extracted_count += _extract_archive_file(file, dst)
    for file in src.iterdir():
        if file.is_file() and file.suffix.lower() in _SUBTITLE_EXTENSIONS:
            extracted_count += _move_raw_subtitle(file, dst)
    return extracted_count


def _move_raw_subtitle(file: Path, dst: Path) -> int:
    target = _resolve_extraction_target(dst, file.name, file.read_bytes())
    if target is None:
        return 0
    dst.mkdir(parents=True, exist_ok=True)
    file.replace(target)
    return 1


def extract_subtitle_by_id(subtitle_id: str, src: Path, dst: Path, extension: str = ".zip") -> int:
    dst.mkdir(parents=True, exist_ok=True)
    extracted_count = 0
    for file in src.glob(f"*{subtitle_id}*{extension}"):
        extracted_count += _extract_archive_file(file, dst)
    return extracted_count


def _is_tested_subtitle(stem: str) -> bool:
    return stem.endswith(_TESTED_MARKER) or f"{_TESTED_MARKER}_v" in stem


def subtitle_files_in(directory: Path) -> list[Path]:
    if not directory.is_dir():
        return []
    return sorted(
        file
        for file in directory.iterdir()
        if file.is_file() and file.suffix.lower() in _SUBTITLE_EXTENSIONS and not _is_tested_subtitle(file.stem)
    )


def count_subtitle_files(directory: Path) -> int:
    return len(subtitle_files_in(directory))


def count_raw_subtitles_by_name(subtitle_name: str, directory: Path) -> int:
    if not directory.is_dir():
        return 0
    return sum(
        1
        for file in directory.iterdir()
        if file.is_file() and file.suffix.lower() in _SUBTITLE_EXTENSIONS and file.stem.startswith(subtitle_name)
    )


def _next_available_path(directory: Path, stem: str, extension: str) -> Path:
    candidate = directory / f"{stem}{extension}"
    version = 1
    while candidate.exists():
        candidate = directory / f"{stem}_v{version}{extension}"
        version += 1
    return candidate


def rename_subtitle_to_release(file_path: Path, release_name: str, extension: str = ".srt") -> Path:
    new_file_path = _next_available_path(file_path.parent, release_name, extension)
    capture(f"Renamed to {new_file_path.name}")
    file_path.rename(new_file_path)
    return new_file_path


def move_all(src: Path, dst: Path) -> int:
    if src.resolve() == dst.resolve():
        return 0
    moved_count = 0
    for file in subtitle_files_in(src):
        destination = _next_available_path(dst, file.stem, file.suffix)
        capture(f"Moving file: {file} -> {destination}")
        file.absolute().replace(destination)
        moved_count += 1
    return moved_count


def move_best_next_to_video(
    source_file: Path, destination_directory: Path, video_stem: str, extraction_directory: Path
) -> None:
    if _is_tested_subtitle(source_file.stem):
        capture(f"Refusing to move already-tested subtitle: {source_file}", level=LogLevel.DEBUG)
        return
    target = destination_directory / f"{video_stem}{source_file.suffix}"
    if target.exists():
        preserved = _next_available_path(extraction_directory, f"{video_stem}{_TESTED_MARKER}", target.suffix)
        capture(f"Preserving existing subtitle: {target} -> {preserved}")
        target.replace(preserved)
    capture(f"Moving file: {source_file} -> {target}")
    source_file.replace(target)


def del_file_type(cwd: Path, extension: str) -> None:
    for file in Path(cwd).glob(f"*{extension}"):
        capture(f"Removing file: {file}")
        file.unlink()


def del_directory(directory: Path) -> None:
    capture(f"Removing directory: {directory}")
    shutil.rmtree(directory)


def delete_path(path: Path) -> None:
    if path.is_dir():
        shutil.rmtree(path, ignore_errors=True)
    elif path.exists():
        path.unlink(missing_ok=True)


def read_json_list(path: Path) -> list[Any]:
    if not path.exists():
        return []
    try:
        return list(json.loads(path.read_text(encoding="utf-8")))
    except json.JSONDecodeError, OSError:
        capture(f"Unreadable list file at {path.name}, starting empty", level=LogLevel.WARNING)
        return []


def write_json_list(path: Path, items: list[Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(items, indent=2), encoding="utf-8")


def read_json_dict(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return dict(json.loads(path.read_text(encoding="utf-8")))
    except json.JSONDecodeError, OSError:
        capture(f"Unreadable dict file at {path.name}, starting empty", level=LogLevel.WARNING)
        return {}


def write_json_dict(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_suffix(f"{path.suffix}.tmp")
    temp_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    temp_path.replace(path)


def directory_is_empty(directory: Path) -> bool:
    if not any(directory.iterdir()):
        return True
    return False


def del_directory_content(directory: Path) -> None:
    for item in directory.iterdir():
        kind = "directory" if item.is_dir() else "file"
        capture(f"Removing {kind}: {item}")
        if item.is_file():
            item.unlink()
        elif item.is_dir():
            shutil.rmtree(item)


def create_directory(path: Path) -> bool:
    if path.exists():
        return False
    capture(f"Creating {path}", level=LogLevel.DEBUG)
    path.mkdir(parents=True, exist_ok=True)
    return True


def get_file_hash(file_path: Path) -> str:
    capture("Calculating hash of video file", level=LogLevel.DEBUG)
    if not file_path.exists():
        return ""

    hash_algorithm = MPCHashAlgorithm(file_path)
    return hash_algorithm.get_hash()


def count_extractable_archives(path: Path, exclude_ids: Collection[str] = frozenset(), extension: str = ".zip") -> int:
    if not path.is_dir():
        return 0
    archives = sum(
        1
        for file in path.glob(f"*{extension}")
        if not any(f"{excluded_id}_" in file.stem for excluded_id in exclude_ids)
    )
    raw_subtitles = sum(1 for file in path.iterdir() if file.is_file() and file.suffix.lower() in _SUBTITLE_EXTENSIONS)
    return archives + raw_subtitles


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
            capture(f"Invalid file size, {self.file_size} bytes", level=LogLevel.WARNING)
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
    response: "CurlResponse",
    on_progress: Callable[[float], None] | None = None,
) -> None:
    start_time = time.time()
    with open(msi_package_path, "wb") as msi_file:
        total_size = int(response.headers.get("content-length", 0))
        downloaded_size = 0
        capture(f"Download started for {msi_package_path.name}")
        capture("Downloading 0.00%")
        for chunk in response.iter_content(chunk_size=128):
            msi_file.write(chunk)
            downloaded_size += len(chunk)
            if total_size > 0:
                progress_percentage = (downloaded_size / total_size) * 100
                if on_progress is not None:
                    on_progress(progress_percentage)
                elapsed_time = time.time() - start_time
                if elapsed_time >= 0.5:
                    capture(f"Downloading {progress_percentage:.2f}%")
                    start_time = time.time()
        if on_progress is not None:
            on_progress(100.0)
        capture("Download complete")
