import logging
import sys
from datetime import datetime
from pathlib import Path

from subsearch.data import __version__, __video__
from subsearch.data.data_fields import FileSearchData, ProviderUrlData, UserConfigData

NOW = datetime.now()
DATE = NOW.strftime("%y%m%d")

if __video__ is None:
    cwd = Path.cwd()
    create_log_file = False
else:
    create_log_file = True
    cwd = __video__.directory

if create_log_file:
    logging.basicConfig(
        filename=Path(cwd) / "subsearch.log",
        filemode="w",
        level=logging.WARNING,
        format="%(asctime)s - %(message)s",
        datefmt="%d-%b-%y %H:%M:%S",
    )


def output(msg: str, to_terminal: bool = True) -> None:
    if create_log_file:
        logging.info(msg)
    if to_terminal:
        print(msg)


def tprint(msg: str) -> None:
    if create_log_file is False:
        return None
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
    output(f"Use HI subtitle:            {user_parameters.hearing_impaired}")
    output(f"Use non-HI subtitle:        {user_parameters.non_hearing_impaired}")
    output(f"Title:                      {param.title}")
    output(f"Year:                       {param.year}")
    output(f"Season:                     {param.season}, {param.season_ordinal}")
    output(f"Episode:                    {param.episode}, {param.episode_ordinal}")
    output(f"Series:                     {param.series}")
    output(f"Release:                    {param.release}")
    output(f"Group:                      {param.group}")
    output(f"Match threshold:            {user_parameters.percentage}%")
    output(f"File hash:                  {param.file_hash}")
    output(f"URL subscene:               {param.url_subscene}")
    output(f"URL openSubtitles - rss:    {param.url_opensubtitles}")
    output(f"URL openSubtitles - hash:   {param.url_opensubtitles_hash}")
    output(f"URL yifysubtitles:          {param.url_yifysubtitles}\n")
