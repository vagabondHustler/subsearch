import os
import shutil
import struct
import zipfile

import cloudscraper

from subsearch.providers.generic import DownloadData
from subsearch.utils import log, string_parser

SCRAPER = cloudscraper.create_scraper(browser={"browser": "chrome", "platform": "android", "desktop": False})


def download_subtitle(data: DownloadData) -> int:
    log.output(f"Downloading: {data.idx_num}/{data.idx_lenght}: {data.name}")
    r = SCRAPER.get(data.url, stream=True)
    with open(data.file_path, "wb") as fd:
        for chunk in r.iter_content(chunk_size=1024):
            fd.write(chunk)

    return data.idx_num


def extract_files(cwd: str, extension: str) -> None:
    subs_folder = os.path.join(cwd, "subs")
    if not os.path.exists(subs_folder):
        os.mkdir(subs_folder)
    for file in os.listdir(cwd):
        if file.startswith("__subsearch__") and file.endswith(extension):
            log.output(f"Extracting: {file} -> ..\\subs\\{file}")
            filename = os.path.join(cwd, file)
            zip_ref = zipfile.ZipFile(filename)
            zip_ref.extractall(subs_folder)
            zip_ref.close()


def rename_best_match(release_name: str, cwd: str, extension: str) -> None:
    higest_value = (0, "")
    subs_folder = os.path.join(cwd, "subs")
    for file in os.listdir(subs_folder):
        if file.endswith(extension):
            value = string_parser.get_pct_value(file, release_name)
            if value >= higest_value[0]:
                higest_value = value, file

    file_to_rename = higest_value[1]
    if file_to_rename.endswith(extension):
        old_name_src = os.path.join(subs_folder, file_to_rename)
        new_name_dst = os.path.join(subs_folder, release_name)
        log.output(f"Renaming: {file_to_rename } -> {release_name}")
        os.rename(old_name_src, new_name_dst)
        move_src = new_name_dst
        move_dst = os.path.join(cwd, release_name)
        log.output(f"Moving: {release_name} -> {cwd}")
        shutil.move(move_src, move_dst)


def clean_up(cwd: str, extension: str) -> None:
    for file in os.listdir(cwd):
        if file.startswith("__subsearch__") and file.endswith(extension):
            log.output(f"Removing: {file}")
            file_path = os.path.join(cwd, file)
            os.remove(file_path)


def write_not_downloaded_tmp(dst: str, not_downloaded: list) -> str:
    file_dst = f"{dst}\\__subsearch__dl_data.tmp"
    with open(file_dst, "w", encoding="utf8") as f:
        for i in range(len(not_downloaded)):
            name, _link = not_downloaded[i][1], not_downloaded[i][2]
            link = _link.replace(" ", "")
            f.writelines(f"{name} {link}")
            f.write("\n")
    return file_dst


def get_hash(file_path: str | None) -> str | None:
    if file_path is None:
        return None
    try:
        longlongformat = "<q"  # little-endian long long
        bytesize = struct.calcsize(longlongformat)
        with open(file_path, "rb") as f:
            filesize = os.path.getsize(file_path)
            hash = filesize
            if filesize < 65536 * 2:
                log.output(f"SizeError: filesize is {filesize} bytes", False)
                return None
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
        log.output("IOError")
        return None
