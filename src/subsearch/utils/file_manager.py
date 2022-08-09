import os
import shutil
import struct
import zipfile

import cloudscraper

from . import log

SCRAPER = cloudscraper.create_scraper(browser={"browser": "chrome", "platform": "android", "desktop": False})


# download zip files from url
def download_zip_auto(item: str) -> None:
    file_path, url, current_num, total_num = item
    log.output(f"Downloading: {current_num}/{total_num}")
    r = SCRAPER.get(url, stream=True)
    with open(file_path, "wb") as fd:
        for chunk in r.iter_content(chunk_size=1024):
            fd.write(chunk)


# extract all zip file in said directory
def extract_zips(cwd_path: str, extension: str) -> None:
    for file in os.listdir(cwd_path):
        if file.startswith("__subsearch__") and file.endswith(extension):
            log.output(f"Extracting: {file}")
            file_name = os.path.join(cwd_path, file)
            # file_name = os.path.abspath(file)
            zip_ref = zipfile.ZipFile(file_name)
            zip_ref.extractall(f"{cwd_path}")
            zip_ref.close()


# rename a .srts to the same as video release name
def rename_srts(new_name: str, cwd: str, group_and_ext: str, extension: str) -> None:
    for file in os.listdir(cwd):
        file_old_name = os.path.join(cwd, file)
        file_new_name = os.path.join(cwd, new_name)
        print(file_old_name, file_new_name)
        if file.endswith(group_and_ext) and os.path.exists(file_new_name) is False:
            log.output(f"Renaming: {file} to {new_name}")
            os.rename(file_old_name, file_new_name)
            return

        elif file.endswith(extension) and os.path.exists(file_new_name) is False:
            log.output(f"Renaming: {file} to {new_name}")
            os.rename(file_old_name, file_new_name)
            return


# move unused .srt to /subs/
def move_files(cwd_path: str, prefered_extension: str, extension: str) -> None:
    for file in os.listdir(cwd_path):
        file = file.lower()
        file_path = os.path.join(cwd_path, file)
        if file.endswith(prefered_extension):
            log.output(f"Keeping: {file}")
            continue
        elif file.endswith(extension) and not file.endswith(prefered_extension):
            dir_subs = os.path.join(cwd_path, "subs")
            dir_sub_file = os.path.join(dir_subs, file)
            if not os.path.exists(dir_subs):
                os.mkdir(dir_subs)
            log.output(f"Moving: {file} to /subs/")
            if os.path.isfile(dir_sub_file):
                os.remove(file_path)
            shutil.move(file_path, dir_sub_file)


# remove .zips
def clean_up(cwd: str, extension: str) -> None:
    for file in os.listdir(cwd):
        if file.startswith("__subsearch__") and file.endswith(extension):
            log.output(f"Removing: {file}")
            file_path = os.path.join(cwd, file)
            os.remove(file_path)


# get file hash
def get_hash(file_name: str) -> str | None:
    try:
        longlongformat = "<q"  # little-endian long long
        bytesize = struct.calcsize(longlongformat)
        with open(file_name, "rb") as f:
            filesize = os.path.getsize(file_name)
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

    except IOError as err:
        return log.output(err)
