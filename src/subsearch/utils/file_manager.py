import os
import shutil
import struct
import zipfile
from typing import Optional

import cloudscraper

from subsearch.scraper.opensubtitles import OpenSubtitlesDownloadData
from subsearch.scraper.subscene import SubsceneDownloadData
from subsearch.utils import log, string_parser

SCRAPER = cloudscraper.create_scraper(browser={"browser": "chrome", "platform": "android", "desktop": False})


def download_zip(download_data: SubsceneDownloadData | OpenSubtitlesDownloadData) -> None:
    log.output(f"Downloading: {download_data.idx_num}/{download_data.idx_lenght}")
    r = SCRAPER.get(download_data.url, stream=True)
    with open(download_data.file_path, "wb") as fd:
        for chunk in r.iter_content(chunk_size=1024):
            fd.write(chunk)


def extract_files(cwd: str, extension: str) -> None:
    # extract all zip file in said directory
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
    # rename a .srts to the same as video release name
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


# remove .zips
def clean_up(cwd: str, extension: str) -> None:
    for file in os.listdir(cwd):
        if file.startswith("__subsearch__") and file.endswith(extension):
            log.output(f"Removing: {file}")
            file_path = os.path.join(cwd, file)
            os.remove(file_path)


# get file hash
def get_hash(file_path: str) -> Optional[str]:
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
