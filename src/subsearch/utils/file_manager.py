import os
import shutil
import struct
import sys
import zipfile
from pathlib import Path

from subsearch.data import video_data
from subsearch.data.data_objects import DownloadMetaData
from subsearch.providers.generic import get_cloudscraper
from subsearch.utils import log, string_parser


def running_from_exe() -> bool:
    """
    Checks if the module is running from an executable file.

    Returns:
        bool: True if the module is running from an executable file, False otherwise.
    """
    if sys.argv[0].endswith(".exe"):
        return True
    return False


def download_subtitle(data: DownloadMetaData) -> int:
    """Download the subtitle from the given url.

    Args:
      data: A DownloadMetaData object that has information about the subtitle file to be downloaded.

    Returns:
      An integer value that represents the index number of the subtitle that was downloaded.

    Raises:
      Any exception raised by the get_cloudscraper or IOError during writing of the subtitle file.
    """
    log.output(f"{data.provider}: {data.idx_num}/{data.idx_lenght}: {data.name}")
    scraper = get_cloudscraper()
    r = scraper.get(data.url, stream=True)
    with open(data.file_path, "wb") as fd:
        for chunk in r.iter_content(chunk_size=1024):
            fd.write(chunk)

    return data.idx_num


def extract_files(src: Path, dst: Path, extension: str) -> None:
    """
    Extract files from a directory to a specified Destination.

    Args:
        src (Path): Source path to extract files
        dst (Path): Destination path to extract files
        extension (str): Extension of files to be extracted

    Returns:
        None.
    """
    for file in os.listdir(src):
        if file.endswith(extension):
            log.output(f"Extracting: {file} -> ..\\subs\\{file}")
            filename = Path(src) / file
            zip_ref = zipfile.ZipFile(filename)
            zip_ref.extractall(dst)
            zip_ref.close()


def rename_best_match(release_name: str, cwd: Path, extension: str) -> None:
    """
    Function renames and moves the best matching subtitle file, based on the release name, to the specified path. If no match is found nothing happens.

    Args:
        release_name (str): The name of the video release whose subtitle is being renamed.
        cwd (Path): The path to the working directory.
        extension (str): The file type of the subtitles i.e ".srt".

    Returns:
        None.
    """
    if video_data is None:
        return None
    higest_value = (0, "")
    for file in os.listdir(video_data.subs_directory):
        if file.endswith(extension):
            value = string_parser.calculate_match(file, release_name)
            if value >= higest_value[0]:
                higest_value = value, file

    file_to_rename = higest_value[1]
    if file_to_rename.endswith(extension):
        old_name_src = Path(video_data.subs_directory) / file_to_rename
        new_name_dst = Path(video_data.subs_directory) / release_name
        log.output(f"Renaming: {file_to_rename } -> {release_name}")
        os.rename(old_name_src, new_name_dst)
        move_src = new_name_dst
        move_dst = Path(cwd) / release_name
        log.output(f"Moving: {release_name} -> {cwd}")
        shutil.move(move_src, move_dst)


def clean_up_files(cwd: Path, extension: str) -> None:
    """
    Removes files with specific extensions in a given directory

    Args:
        cwd (pathlib.Path): The directory path where the files to be deleted reside.
        extension (str): The file extension of the files to be deleted.

    Returns:
        None
    """

    for file in os.listdir(cwd):
        if file.endswith(extension):
            log.output(f"Removing: {file}")
            file_path = Path(cwd) / file
            file_path.unlink()


def del_directory(directory: Path) -> None:
    """
    Remove a directory and its contents.

    Args:
        directory: A Path object representing the directory to be removed.

    Returns:
        None
    """
    for file in os.listdir(directory):
        log.output(f"Removing: {file}")
    log.output(f"Removing: {directory}")
    shutil.rmtree(directory)


def directory_is_empty(directory: Path) -> bool:
    if len(os.listdir(directory)) == 0:
        return True
    return False


def make_necessary_directories() -> None:
    """
    Make necessary directories using video object info.
    """

    if video_data is None:
        return None
    if not Path(video_data.tmp_directory).exists():
        Path.mkdir(video_data.tmp_directory)
    if not Path(video_data.subs_directory).exists():
        Path.mkdir(video_data.subs_directory)


def get_hash(file_path: Path | None) -> str:
    """
    Calculates and returns the hash value of given file path.

    Args:
        file_path: A Path object indicating the location of the input file. If None, returns an all-zero string.

    Returns:
        A hexadecimal String indicating the unique hash value of the file. If the file cannot be read or its size is less than 131072 bytes, returns an all-zero string '000000000000000000'.

    Examples:
        get_hash(Path("my_folder/my_file.jpg")) returns "d020f52c464caedd"
        get_hash(None) returns "000000000000000000"
    """
    if file_path is None:
        return "000000000000000000"
    try:
        longlongformat = "<q"  # little-endian long long
        bytesize = struct.calcsize(longlongformat)
        with open(file_path, "rb") as f:
            filesize = os.path.getsize(file_path)
            hash = filesize
            if filesize < 65536 * 2:
                log.output(f"SizeError: filesize is {filesize} bytes", False)
                return "000000000000000000"
            n1 = 65536 // bytesize
            for _x in range(n1):
                buffer = f.read(bytesize)
                (l_value,) = struct.unpack(longlongformat, buffer)
                hash += l_value
                hash = hash & 0xFFFFFFFFFFFFFFFF  # to remain as 64bit number
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
        return "000000000000000000"
