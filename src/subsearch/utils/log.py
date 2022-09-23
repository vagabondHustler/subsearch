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


class SubsearchOutputs:
    def __init__(self):
        ...

    def app_parameters(self, fsd: FileSearchData, ucd: UserConfigData, pud: ProviderUrlData) -> None:
    # log and print all the used parameters from video/directory-name
    output(f"[PARAMETERS]                [VALUES]")
        output(f"Subsearch:                  v{__version__} ")
        output(f"Language:                   {ucd.current_language}, {ucd.language_code3}")
        output(f"Use HI subtitle:            {ucd.hearing_impaired}")
        output(f"Use non-HI subtitle:        {ucd.non_hearing_impaired}")
        output(f"Title:                      {fsd.title}")
        output(f"Year:                       {fsd.year}")
        output(f"Season:                     {fsd.season}, {fsd.season_ordinal}")
        output(f"Episode:                    {fsd.episode}, {fsd.episode_ordinal}")
        output(f"Series:                     {fsd.series}")
        output(f"Release:                    {fsd.release}")
        output(f"Group:                      {fsd.group}")
        output(f"Match threshold:            {ucd.percentage}%")
        output(f"File hash:                  {fsd.file_hash}")
        output(f"URL subscene - site:        {pud.subscene}")
        output(f"URL opensubtitles - site:   {pud.opensubtitles}")
        output(f"URL openSubtitles - hash:   {pud.opensubtitles_hash}")
        output(f"URL yifysubtitles - site:   {pud.yifysubtitles}")
        output("\n")

    def match(self, pct_result: int, key: str):
        output(f"{pct_result:>3}% match: {key}")

    def done_with_tasks(self, end_new_line: bool = False):
        output("Done with tasks")
        if end_new_line:
            output("\n")

