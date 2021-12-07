import requests
import os
import zipfile
import shutil


def download_zip(zip_path: str, zip_url: str) -> None:
    r = requests.get(zip_url, stream=True)
    with open(zip_path, "wb") as fd:
        for chunk in r.iter_content(chunk_size=128):
            fd.write(chunk)


def extract_zips(cwd_path: str, extension: str) -> None:
    for file in os.listdir(cwd_path):
        if file.endswith(extension):
            file_name = os.path.abspath(file)
            zip_ref = zipfile.ZipFile(file_name)
            zip_ref.extractall(f"{cwd_path}")
            zip_ref.close()


def rename_srts(new_name: str, cwd_path: str, prefered_extension: str, extension: str) -> None:
    for file in os.listdir(cwd_path):
        if file.endswith(prefered_extension) and os.path.exists(new_name) is False:
            os.rename(file, new_name)
            return

        elif file.endswith(extension) and os.path.exists(new_name) is False:
            os.rename(file, new_name)
            return


def move_files(cwd_path: str, prefered_extension: str, extension: str) -> None:
    dir_subs = "subs/"
    os.mkdir(dir_subs) if os.path.exists(dir_subs) is False else None
    for file in os.listdir(cwd_path):
        if file.endswith(prefered_extension):
            pass
        elif file.endswith(extension):
            os.remove(f"subs/{file}") if os.path.exists(f"subs/{file}") else None
            shutil.move(file, f"subs/{file}")


def clean_up(cwd_path: str, extension: str) -> None:
    for file in os.listdir(cwd_path):
        if file.endswith(extension):
            os.remove(file)
