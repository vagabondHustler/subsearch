import shutil
import struct
import time
import traceback
import zipfile
from io import BufferedReader
from pathlib import Path
from typing import Callable, Iterable, Optional

import requests

from subsearch.runtime.logging.logger import log
from subsearch.runtime.config.constants import VIDEO_FILE
from subsearch.runtime.models.model import Subtitle
from subsearch.io.http import get_session
from subsearch.parsing import release_parser


def create_path_from_string(string: str, path_resolution: str, create_missing_folder: bool = True) -> Path:
    path = VIDEO_FILE.file_directory
    if path_resolution == "relative":
        if string == ".":
            path = VIDEO_FILE.file_directory
        elif string.startswith(".\\") and len(string) > 2:
            path = VIDEO_FILE.file_directory.joinpath(string[2:])
        elif string == "..":
            path = VIDEO_FILE.file_directory.parent
        elif string.startswith("..\\") and len(string) > 3:
            path = VIDEO_FILE.file_directory.parent.joinpath(string[3:])
    elif path_resolution == "absolute":
        path = Path(string)

    if not path.is_dir() and not create_missing_folder:
        log.warning(f"Destination folder {path} does not exist, moving to {VIDEO_FILE.file_directory} instead")
        return VIDEO_FILE.file_directory

    path.mkdir(parents=True, exist_ok=True)
    return path


_ZIP_MAGIC_BYTES = (b"PK\x03\x04", b"PK\x05\x06", b"PK\x07\x08")


def is_zip_payload(chunk: bytes) -> bool:
    return chunk.startswith(_ZIP_MAGIC_BYTES)


def download_subtitle(subtitle: Subtitle, index_position: int, index_size: int) -> None:
    log.info(f"{subtitle.provider_name}: {index_position}/{index_size}: {subtitle.subtitle_name}")
    session = get_session()
    response = session.get(subtitle.download_url, headers=subtitle.download_headers, stream=True)
    file_name = f"{subtitle.provider_name}_{subtitle.subtitle_name}_{index_position}.zip"
    download_path = VIDEO_FILE.tmp_dir / file_name
    chunks = response.iter_content(chunk_size=1024)
    first_chunk = next(chunks, b"")
    if not is_zip_payload(first_chunk):
        log.warning(f"{subtitle.provider_name}: {subtitle.subtitle_name} is not a zip, skipping download")
        return
    with open(download_path, "wb") as fd:
        fd.write(first_chunk)
        for chunk in chunks:
            fd.write(chunk)


_SUBTITLE_EXTENSIONS = {".srt", ".sub", ".ass", ".ssa", ".vtt"}
_MAX_UNCOMPRESSED_BYTES = 50 * 1024 * 1024  # 50 MB , generous for any subtitle archive


def _safe_extract_archive(archive: zipfile.ZipFile, dst: Path) -> None:
    total_uncompressed = sum(info.file_size for info in archive.infolist())
    if total_uncompressed > _MAX_UNCOMPRESSED_BYTES:
        log.warning(f"Archive uncompressed size {total_uncompressed} exceeds limit, skipping")
        return

    dst_resolved = dst.resolve()
    for member in archive.infolist():
        member_path = (dst / member.filename).resolve()
        if not str(member_path).startswith(str(dst_resolved)):
            log.warning(f"Skipping unsafe path in archive: {member.filename}")
            continue
        if member_path.suffix.lower() not in _SUBTITLE_EXTENSIONS:
            continue
        archive.extract(member, dst)


def extract_files_in_dir(src: Path, dst: Path, extension: str = ".zip") -> None:
    for file in src.glob(f"*{extension}"):
        log.event("extract", src=file, dst=dst)
        try:
            with zipfile.ZipFile(file) as archive:
                _safe_extract_archive(archive, dst)
        except zipfile.BadZipFile, OSError:
            log.error(f"Skipping unreadable archive {file.name}\n{traceback.format_exc()}")


def find_best_subtitle_match(release_name: str, extension: str = ".srt") -> Path:
    best_match = (0, Path("."))
    for file in VIDEO_FILE.subs_dir.glob(f"*{extension}"):
        value = release_parser.calculate_match(file.name, release_name)
        if value >= best_match[0]:
            best_match = value, file
    return best_match[1]


def rename_subtitle_to_release(file_path: Path, release_name: str, extension: str = ".srt") -> Path:
    new_file_path = file_path.with_name(f"{release_name}{extension}")
    log.event("rename", src=file_path, dst=new_file_path)
    file_path.rename(new_file_path)
    return new_file_path


def autoload_rename(release_name: str, extension: str = ".srt") -> Path:
    matched_file = find_best_subtitle_match(release_name, extension)
    return rename_subtitle_to_release(matched_file, release_name, extension)


def move_all(src: Path, dst: Path, extension: str = ".srt") -> None:
    for file in src.glob(f"*{extension}"):
        move_and_replace(file.absolute(), dst)


def move_and_replace(source_file: Path, destination_directory: Path) -> None:
    source_file.replace(destination_directory / source_file.name)
    log.event("move", src=source_file, dst=destination_directory)


def del_file_type(cwd: Path, extension: str) -> None:
    for file in Path(cwd).glob(f"*{extension}"):
        log.event("remove", src=file)
        file.unlink()


def del_directory(directory: Path) -> None:
    log.event("remove", src=directory)
    shutil.rmtree(directory)


def directory_is_empty(directory: Path) -> bool:
    if not any(directory.iterdir()):
        return True
    return False


def del_directory_content(directory: Path) -> None:
    for item in directory.iterdir():
        log.event("remove", src=item)
        if item.is_file():
            item.unlink()
        elif item.is_dir():
            shutil.rmtree(item)


def create_directory(path: Path) -> None:
    if path.exists():
        return None
    log.debug(f"Creating {path}")
    path.mkdir(parents=True, exist_ok=True)


def get_file_hash(file_path: Path) -> str:
    log.debug("Calculating hash of video file")
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
    def __init__(self, file_path: Path, **kwargs) -> None:
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
            log.warning(f"Invalid file size, {self.file_size} bytes")
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
    response: requests.Response,
    on_progress: Callable[[float], None] | None = None,
) -> None:
    start_time = time.time()
    with open(msi_package_path, "wb") as msi_file:
        total_size = int(response.headers.get("content-length", 0))
        downloaded_size = 0
        log.info(f"Download started for {msi_package_path.name}")
        log.info(f"Downloading 0%")
        for chunk in response.iter_content(chunk_size=128):
            msi_file.write(chunk)
            downloaded_size += len(chunk)
            if total_size > 0:
                progress_percentage = (downloaded_size / total_size) * 100
                if on_progress is not None:
                    on_progress(progress_percentage)
                elapsed_time = time.time() - start_time
                if elapsed_time >= 0.5:
                    log.info(f"Downloading {progress_percentage:.2f}%")
                    start_time = time.time()
        if on_progress is not None:
            on_progress(100.0)
        log.info(f"Download complete.")
