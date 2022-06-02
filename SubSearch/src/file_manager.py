import os
import shutil
import struct
import zipfile

import cloudscraper

SCRAPER = cloudscraper.create_scraper(browser={"browser": "chrome", "platform": "android", "desktop": False})

from src import log
from src.sos import cwd, root_directory_file


# check if a video is in directory, returns video name without extension
def find_video(cwd_path: str, video_ext: list, with_ext: bool) -> str:
    for file in os.listdir(cwd_path):
        for ext in video_ext:
            if file.endswith(ext):
                video_release_name_ext = file.replace(f"{ext}", "")
                video_release_name = video_release_name_ext.lower()
                if with_ext:
                    return file
                elif with_ext is False:
                    return video_release_name
    return None


# download zip files from url
def download_zip(item: str) -> None:
    file_path, url, current_num, total_num = item
    log.output(f"Downloading: {current_num}/{total_num}")
    r = SCRAPER.get(url, stream=True)
    with open(file_path, "wb") as fd:
        for chunk in r.iter_content(chunk_size=1024):
            fd.write(chunk)


# extract all zip file in said directory
def extract_zips(cwd_path: str, extension: str) -> None:
    for file in os.listdir(cwd_path):
        if file.endswith(extension):
            log.output(f"Extracting: {file}")
            file_name = os.path.abspath(file)
            zip_ref = zipfile.ZipFile(file_name)
            zip_ref.extractall(f"{cwd_path}")
            zip_ref.close()


# rename a .srts to the same as video release name
def rename_srts(new_name: str, cwd_path: str, prefered_extension: str, extension: str) -> None:
    for file in os.listdir(cwd_path):
        if file.endswith(prefered_extension) and os.path.exists(new_name) is False:
            log.output(f"Renaming: {file} to {new_name}")
            os.rename(file, new_name)
            return

        elif file.endswith(extension) and os.path.exists(new_name) is False:
            log.output(f"Renaming: {file} to {new_name}")
            os.rename(file, new_name)
            return


# move unused .srts to /subs/
def move_files(cwd_path: str, prefered_extension: str, extension: str) -> None:
    for file in os.listdir(cwd_path):
        file = file.lower()
        if file.endswith(prefered_extension):
            log.output(f"Keeping: {file}")
            continue
        elif file.endswith(extension) and not file.endswith(prefered_extension):
            dir_subs = "subs/"
            os.mkdir(dir_subs) if os.path.exists(dir_subs) is False else None
            log.output(f"Moving: {file} to /subs/")
            os.remove(f"subs/{file}") if os.path.exists(f"subs/{file}") else None
            shutil.move(file, f"subs/{file}")


# remove .zips
def clean_up(cwd_path: str, extension: str) -> None:
    for file in os.listdir(cwd_path):
        if file.endswith(extension):
            log.output(f"Removing: {file}")
            os.remove(file)


def copy_log_to_cwd() -> None:
    src_file = root_directory_file("search.log")
    dst_file = f"{cwd()}/search.log"
    shutil.copy(src_file, dst_file)


def get_hash(file_name: str):
    try:
        longlongformat = "<q"  # little-endian long long
        bytesize = struct.calcsize(longlongformat)
        with open(file_name, "rb") as f:
            filesize = os.path.getsize(file_name)
            hash = filesize
            if filesize < 65536 * 2:
                log.output(f"SizeError: {filesize} bytes", False)
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

    except IOError as err:
        return log.output(err)
