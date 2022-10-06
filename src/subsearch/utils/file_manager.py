import os
import shutil
import struct
import zipfile
from pathlib import Path

import cloudscraper

from subsearch.data import __video__
from subsearch.data.data_fields import DownloadData
from subsearch.utils import log, string_parser

SCRAPER = cloudscraper.create_scraper(browser={"browser": "chrome", "platform": "android", "desktop": False})


def download_subtitle(data: DownloadData) -> int:
    log.output(f"{data.provider}: {data.idx_num}/{data.idx_lenght}: {data.name}")
    r = SCRAPER.get(data.url, stream=True)
    with open(data.file_path, "wb") as fd:
        for chunk in r.iter_content(chunk_size=1024):
            fd.write(chunk)

    return data.idx_num


def extract_files(src: Path, dst: Path, extension: str) -> None:
    for file in os.listdir(src):
        if file.endswith(extension):
            log.output(f"Extracting: {file} -> ..\\subs\\{file}")
            filename = Path(src) / file
            zip_ref = zipfile.ZipFile(filename)
            zip_ref.extractall(dst)
            zip_ref.close()


def rename_best_match(release_name: str, cwd: Path, extension: str) -> None:
    if __video__ is None:
        return None
    higest_value = (0, "")
    for file in os.listdir(__video__.subs_directory):
        if file.endswith(extension):
            value = string_parser.get_pct_value(file, release_name)
            if value >= higest_value[0]:
                higest_value = value, file

    file_to_rename = higest_value[1]
    if file_to_rename.endswith(extension):
        old_name_src = Path(__video__.subs_directory) / file_to_rename
        new_name_dst = Path(__video__.subs_directory) / release_name
        log.output(f"Renaming: {file_to_rename } -> {release_name}")
        os.rename(old_name_src, new_name_dst)
        move_src = new_name_dst
        move_dst = Path(cwd) / release_name
        log.output(f"Moving: {release_name} -> {cwd}")
        shutil.move(move_src, move_dst)


def clean_up_files(cwd: Path, extension: str) -> None:
    for file in os.listdir(cwd):
        if file.endswith(extension):
            log.output(f"Removing: {file}")
            file_path = Path(cwd) / file
            file_path.unlink()


def del_directory(directory: Path) -> None:
    for file in os.listdir(directory):
        log.output(f"Removing: {file}")
    log.output(f"Removing: {directory}")
    shutil.rmtree(directory)


def make_necessary_directories():
    if __video__ is None:
        return None
    if not Path(__video__.tmp_directory).exists():
        Path.mkdir(__video__.tmp_directory)
    if not Path(__video__.subs_directory).exists():
        Path.mkdir(__video__.subs_directory)


def get_hash(file_path: Path | None) -> str:
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
