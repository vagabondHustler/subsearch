import logging
import warnings
from datetime import datetime
from pathlib import Path

from subsearch.data import __version__, __video__
from subsearch.data.data_fields import (
    FormattedData,
    ProviderUrlData,
    ReleaseData,
    UserData,
)
from subsearch.utils import raw_config

NOW = datetime.now()
DATE = NOW.strftime("%y%m%d")
LOG_TO_FILE = raw_config.get_config_key("log_to_file")

release_data: ReleaseData
user_data: UserData
url_data: ProviderUrlData

logger = logging.getLogger("subsearch")
logger.setLevel(logging.DEBUG)

if __video__ is not None and LOG_TO_FILE:
    warnings.filterwarnings("ignore", lineno=545)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", datefmt="%d-%b-%y %H:%M:%S")
    file_handler = logging.FileHandler(Path(__video__.directory) / "subsearch.log", "w")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


def output(msg: str, terminal: bool = True, to_log: bool = True, level: str = "info"):
    def _to_log(msg: str, level: str) -> None:
        if __video__ is None or LOG_TO_FILE is False:
            return None
        if to_log is False:
            return None
        if level == "info":
            logger.info(msg)
        elif level == "warning":
            logger.warning(msg)
        elif level == "error":
            logger.error(msg)
        elif level == "critical":
            logger.critical(msg)

    def _to_terminal(msg: str, to_terminal, level: str) -> None:
        if to_terminal is False:
            return None
        if level == "info":
            print(msg)
        else:
            print(f"{level.upper()} - {msg}")

    _to_log(msg, level)
    _to_terminal(msg, terminal, level)


def warning_spaces_in_filename():
    name_unresolved = f"{__video__.name}{__video__.ext}"
    output(f"File: '{name_unresolved}' contains spaces", level="warning")
    output(f"Results may vary, use punctuation marks for a more accurate result", level="info")
    output("")


def output_header(msg: str):
    output(f"--- [{msg}] ---")


def output_skip_provider(provider: str, reason: str):
    output("")
    output_header(f"Skipping {provider}")
    output(f"{reason}")
    output("Done with tasks")
    output("")


def output_done_with_tasks(end_new_line: bool = False):
    output("Done with tasks")
    if end_new_line:
        output("")


def output_parameters() -> None:
    output_header(f"User data")
    output(f"Language:                         {user_data.current_language}, {user_data.language_code3}")
    output(f"Use HI subtitle:                  {user_data.hearing_impaired}")
    output(f"Use non-HI subtitle:              {user_data.non_hearing_impaired}")
    output(f"Match threshold:                  {user_data.percentage}%")
    output(f"Use site subscene:                {user_data.providers['subscene_site']}")
    output(f"Use site opensubtitles:           {user_data.providers['opensubtitles_site']}")
    output(f"Use hash opensubtitles:           {user_data.providers['opensubtitles_hash']}")
    output(f"Use site yifysubtitles:           {user_data.providers['subscene_site']}")
    output("")
    output_header(f"File data")
    output(f"Filename:                         {__video__.name}")
    output(f"Directory:                        {__video__.directory}")
    output("")
    output_header(f"Release data")
    output(f"Title:                            {release_data.title}")
    output(f"Year:                             {release_data.year}")
    output(f"Season:                           {release_data.season}, {release_data.season_ordinal}")
    output(f"Episode:                          {release_data.episode}, {release_data.episode_ordinal}")
    output(f"Series:                           {release_data.series}")
    output(f"Release:                          {release_data.release}")
    output(f"Group:                            {release_data.group}")
    output(f"File hash:                        {release_data.file_hash}")
    output("")
    output_header(f"Provider url data")
    output(f"subscene_site:                    {url_data.subscene}")
    output(f"opensubtitles_site:               {url_data.opensubtitles}")
    output(f"openSubtitles_hash:               {url_data.opensubtitles_hash}")
    output(f"yifysubtitles_site:               {url_data.yifysubtitles}")
    output("")


def output_match(provider: str, pct_result: int, key: str, _to_log: bool = False):
    if pct_result >= user_data.percentage:
        output(f"> {provider:<14}{pct_result:>3}% {key}", to_log=_to_log)
    else:
        output(f"  {provider:<14}{pct_result:>3}% {key}", to_log=_to_log)


def set_logger_data(rd: ReleaseData, ud: UserData, pud: ProviderUrlData):
    global release_data, user_data, url_data
    release_data = rd
    user_data = ud
    url_data = pud
