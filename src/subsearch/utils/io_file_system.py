import shutil
import struct
import time
import zipfile
from io import BufferedReader
from pathlib import Path
from typing import Iterable, Optional

import requests

from subsearch.globals import log
from subsearch.globals.constants import VIDEO_FILE
from subsearch.globals.dataclasses import Subtitle
from subsearch.providers.common_utils import get_cloudscraper
from subsearch.utils import string_parser


def create_path_from_string(string: str, path_resolution: str) -> Path:
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

    path.mkdir(parents=True, exist_ok=True)
    return path


def download_subtitle(subtitle: Subtitle, index_position: int, index_size: int) -> None:
    log.stdout(f"{subtitle.provider_name}: {index_position}/{index_size}: {subtitle.subtitle_name}")
    scraper = get_cloudscraper()
    r = scraper.get(subtitle.download_url, stream=True)
    file_name = f"{subtitle.provider_name}_{subtitle.subtitle_name}_{index_position}.zip"
    download_path = VIDEO_FILE.tmp_dir / file_name
    with open(download_path, "wb") as fd:
        for chunk in r.iter_content(chunk_size=1024):
            fd.write(chunk)


def extract_files_in_dir(src: Path, dst: Path, extension: str = ".zip") -> None:
    for file in src.glob(f"*{extension}"):
        filename = src / file
        log.file_system_action(action_type="extract", src=file, dst=dst)
        zip_ref = zipfile.ZipFile(filename)
        zip_ref.extractall(dst)
        zip_ref.close()


def autoload_rename(release_name: str, extension: str = ".srt") -> Path:
    best_match = (0, Path("."))
    for file in VIDEO_FILE.subs_dir.glob(f"*{extension}"):
        value = string_parser.calculate_match(file.name, release_name)
        if value >= best_match[0]:
            best_match = value, file

    old_file_path = best_match[1]
    new_file_path = old_file_path.with_name(f"{release_name}{extension}")
    log.file_system_action(action_type="rename", src=old_file_path, dst=new_file_path)
    old_file_path.rename(new_file_path)
    return new_file_path


def move_all(src: Path, dst: Path, extension: str = ".srt") -> None:
    for file in src.glob(f"*{extension}"):
        move_and_replace(file.absolute(), dst)


def move_and_replace(source_file: Path, destination_directory: Path) -> None:
    source_file.replace(destination_directory / source_file.name)
    log.file_system_action(action_type="move", src=source_file, dst=destination_directory)


def del_file_type(cwd: Path, extension: str) -> None:
    for file in Path(cwd).glob(f"*{extension}"):
        log.file_system_action(action_type="remove", src=file)
        file_path = Path(cwd) / file
        file_path.unlink()


def del_directory(directory: Path) -> None:
    log.file_system_action(action_type="remove", src=directory)
    shutil.rmtree(directory)


def directory_is_empty(directory: Path) -> bool:
    if not any(directory.iterdir()):
        return True
    return False


def del_directory_content(directory: Path) -> None:
    for item in directory.iterdir():
        if not item.is_file():
            return None
        log.file_system_action(action_type="remove", src=item)
        if item.is_file():
            item.unlink()
        if item.is_dir():
            shutil.rmtree(item)


def create_directory(path: Path) -> None:
    if path.exists():
        return None
    log.stdout(f"Creating {path}", level="debug")
    path.mkdir(parents=True, exist_ok=True)


def get_file_hash(file_path: Path) -> str:
    log.stdout("Calculating hash of video file", level="debug")
    if not file_path:
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
            log.stdout(f"Invalid file size, {self.file_size} bytes", level="warning")
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


def download_response(msi_package_path: Path, response: requests.Response) -> None:
    start_time = time.time()
    with open(msi_package_path, "wb") as msi_file:
        total_size = int(response.headers.get("content-length", 0))
        downloaded_size = 0
        log.stdout(f"Download started for {msi_package_path.name}")
        log.stdout(f"Downloading 0%")
        for chunk in response.iter_content(chunk_size=128):
            msi_file.write(chunk)
            downloaded_size += len(chunk)
            progress_percentage = (downloaded_size / total_size) * 100
            elapsed_time = time.time() - start_time
            if elapsed_time >= 0.5:
                log.stdout(f"Downloading {progress_percentage:.2f}%")
                start_time = time.time()
        log.stdout(f"Download complete.")
