import logging
from datetime import datetime

from src.util import local_paths, version

now = datetime.now()
date = now.strftime("%y%m%d")

if local_paths.get_path("cwd") == local_paths.get_path("root"):
    logging.basicConfig(
        filename=f"__subsearch__.log",
        filemode="w",
        level=logging.DEBUG,
        format="%(asctime)s - %(message)s",
        datefmt="%d-%b-%y %H:%M:%S",
    )

# log and print message
def output(msg: str, print_to_terminal: bool = True):
    logging.info(msg)
    print(msg) if print_to_terminal else False


# log and print all the used parameters from video/directory-name
def parameters(param: str, language: str, lang_abbr: str, hearing_impaired: str, percentage: int):
    current_version = version.current()
    output(f"SubSearch - {current_version} ", False)
    output("[PARAMETERS]")
    output(f"Language: {language}, {lang_abbr}")
    output(f"Hearing impaired: {hearing_impaired}")
    output(f"Title: {param.title}")
    output(f"Year: {param.year}")
    output(f"Season: {param.season}, {param.season_ordinal}")
    output(f"Episode: {param.episode}, {param.episode_ordinal}")
    output(f"TV-Series: {param.tv_series}")
    output(f"Release: {param.release}")
    output(f"Group: {param.group}")
    output(f"Match threshold: {percentage}%")
    output(f"File hash: {param.file_hash}")
    output(f"URL: {param.url_subscene}")
    output(f"URL: {param.url_opensubtitles}\n")
