import logging
import os
import sys
from datetime import datetime
from typing import Literal, Optional

from subsearch.data import __version__, __video_directory__
from subsearch.utils.string_parser import SearchParameters

CWD = os.getcwd()
if __video_directory__ is not None:
    CWD = __video_directory__


NOW = datetime.now()
DATE = NOW.strftime("%y%m%d")

logging.basicConfig(
    filename=f"{CWD}\\__subsearch__.log",
    filemode="w",
    level=logging.DEBUG,
    format="%(asctime)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
)

# log and print message
def output(msg: str, to_terminal: bool = True) -> Optional[Literal[False]]:
    logging.info(msg)
    return print(msg) if to_terminal else False


def tprint(msg: str) -> None:
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    root.addHandler(handler)
    return logging.info(msg)


# log and print all the used parameters from video/directory-name
def parameters(param: SearchParameters, lang: str, lang_code2: str, hearing_impaired: str, pct: int) -> None:
    lang_code3 = lang[:3].lower()
    output(f"SubSearch - {__version__} ", False)
    output("[PARAMETERS]")
    output(f"Language: {lang}, {lang_code2}, {lang_code3}")
    output(f"Hearing impaired: {hearing_impaired}")
    output(f"Title: {param.title}")
    output(f"Year: {param.year}")
    output(f"Season: {param.season}, {param.season_ordinal}")
    output(f"Episode: {param.episode}, {param.episode_ordinal}")
    output(f"TV-Series: {param.show_bool}")
    output(f"Release: {param.release}")
    output(f"Group: {param.group}")
    output(f"Match threshold: {pct}%")
    output(f"File hash: {param.file_hash}")
    output(f"URL: {param.url_subscene}")
    output(f"URL: {param.url_opensubtitles}\n")
