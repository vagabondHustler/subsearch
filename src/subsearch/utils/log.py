import logging
import os
import sys
from datetime import datetime
from typing import Literal

from subsearch.data import __version__, __video__
from subsearch.utils import raw_config
from subsearch.utils.raw_config import UserParameters
from subsearch.utils.string_parser import FileSearchParameters

CWD = os.getcwd()
if __video__.directory is not None:
    CWD = __video__.directory


NOW = datetime.now()
DATE = NOW.strftime("%y%m%d")

logging.basicConfig(
    filename=f"{CWD}\\__subsearch__.log",
    filemode="w",
    level=logging.DEBUG,
    format="%(asctime)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
)


def output(msg: str, to_terminal: bool = True) -> Literal[False] | None:
    # log and print message
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


def parameters(param: FileSearchParameters, user_parameters: UserParameters) -> None:
    # log and print all the used parameters from video/directory-name
    languages = raw_config.get_config_key("languages")
    lang_code3 = languages[user_parameters.current_language]
    output(f"[PARAMETERS]                [VALUES]")
    output(f"subsearch:                  v{__version__} ")
    output(f"Language:                   {user_parameters.current_language}, {lang_code3}")
    output(f"Hearing impaired:           {user_parameters.hearing_impaired}")
    output(f"Title:                      {param.title}")
    output(f"Year:                       {param.year}")
    output(f"Season:                     {param.season}, {param.season_ordinal}")
    output(f"Episode:                    {param.episode}, {param.episode_ordinal}")
    output(f"Series:                     {param.series}")
    output(f"Release:                    {param.release}")
    output(f"Group:                      {param.group}")
    output(f"Match threshold:            {user_parameters.pct}%")
    output(f"File hash:                  {param.file_hash}")
    output(f"URL Subscene:               {param.url_subscene}")
    output(f"URL OpenSubtitles - rss:    {param.url_opensubtitles}")
    output(f"URL OpenSubtitles - hash:   {param.url_opensubtitles_hash}\n")
