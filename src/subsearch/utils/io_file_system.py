import shutil
import struct
import zipfile
from pathlib import Path

from subsearch.data.constants import VIDEO_FILE
from subsearch.data.data_classes import Subtitle
from subsearch.providers.core_provider import get_cloudscraper
from subsearch.utils import io_log, string_parser


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


def download_subtitle(subtitle: Subtitle, index_position: int, index_size: int):
    io_log.stdout(f"{subtitle.provider}: {index_position}/{index_size}: {subtitle.release_name}")
    scraper = get_cloudscraper()
    r = scraper.get(subtitle.download_url, stream=True)
    file_name = f"{subtitle.provider}_{subtitle.release_name}_{index_position}.zip"
    download_path = VIDEO_FILE.tmp_dir / file_name
    with open(download_path, "wb") as fd:
        for chunk in r.iter_content(chunk_size=1024):
            fd.write(chunk)


def extract_files_in_dir(src: Path, dst: Path, extension: str = ".zip") -> None:
    for file in src.glob(f"*{extension}"):
        filename = src / file
        io_log.stdout_path_action(action_type="extract", src=file, dst=dst)
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
    io_log.stdout_path_action(action_type="rename", src=old_file_path, dst=new_file_path)
    old_file_path.rename(new_file_path)
    return new_file_path


def move_all(src: Path, dst: Path, extension: str = ".srt"):
    for file in src.glob(f"*{extension}"):
        move_and_replace(file.absolute(), dst)


def move_and_replace(source_file: Path, destination_directory: Path) -> None:
    source_file.replace(destination_directory / source_file.name)


def del_file_type(cwd: Path, extension: str) -> None:
    for file in Path(cwd).glob(f"*{extension}"):
        io_log.stdout_path_action(action_type="remove", src=file)
        file_path = Path(cwd) / file
        file_path.unlink()


def del_directory(directory: Path) -> None:
    io_log.stdout_path_action(action_type="remove", src=directory)
    shutil.rmtree(directory)


def directory_is_empty(directory: Path) -> bool:
    if not any(directory.iterdir()):
        return True
    return False


def del_directory_content(directory: Path):
    for item in directory.iterdir():
        io_log.stdout_path_action(action_type="remove", src=item)
        if item.is_file():
            item.unlink()
        if item.is_dir():
            shutil.rmtree(item)


def create_directory(path: Path):
    path.mkdir(exist_ok=True)


def get_file_hash(file_path: Path | None) -> str:
    if file_path is None:
        return ""
    try:
        longlongformat = "<q"
        bytesize = struct.calcsize(longlongformat)
        with open(file_path, "rb") as f:
            filesize = file_path.stat().st_size
            hash = filesize
            if filesize < 65536 * 2:
                io_log.stdout(f"SizeError: filesize is {filesize} bytes", level="error")
                return ""
            n1 = 65536 // bytesize
            for _x in range(n1):
                buffer = f.read(bytesize)
                (l_value,) = struct.unpack(longlongformat, buffer)
                hash += l_value
                hash = hash & 0xFFFFFFFFFFFFFFFF
            f.seek(max(0, filesize - 65536), 0)
            n2 = 65536 // bytesize
            for _x in range(n2):
                buffer = f.read(bytesize)
                (l_value,) = struct.unpack(longlongformat, buffer)
                hash += l_value
                hash = hash & 0xFFFFFFFFFFFFFFFF

        returnedhash = "%016x" % hash
        return returnedhash

    except IOError:
        return ""
