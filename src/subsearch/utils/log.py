import logging
import warnings
from datetime import datetime
from pathlib import Path

from subsearch.data import __version__, __video__
from subsearch.data.data_objects import (
    AppConfig,
    FormattedMetadata,
    ProviderUrls,
    ReleaseMetadata,
)
from subsearch.utils import raw_config

NOW = datetime.now()
DATE = NOW.strftime("%y%m%d")
LOG_TO_FILE = raw_config.get_config_key("log_to_file")

release_metadata: ReleaseMetadata
app_config: AppConfig
provider_urls: ProviderUrls

logger = logging.getLogger("subsearch")
logger.setLevel(logging.DEBUG)

if __video__ is not None and LOG_TO_FILE:
    warnings.filterwarnings("ignore", lineno=545)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", datefmt="%d-%b-%y %H:%M:%S")
    file_handler = logging.FileHandler(Path(__video__.directory_path) / "subsearch.log", "w")
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
    name_unresolved = f"{__video__.filename}{__video__.file_extension}"
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
    output(f"Language:                         {app_config.current_language}, {app_config.language_iso_639_3}")
    output(f"Use HI subtitle:                  {app_config.hearing_impaired}")
    output(f"Use non-HI subtitle:              {app_config.non_hearing_impaired}")
    output(f"Match threshold:                  {app_config.percentage_threshold}%")
    output(f"Use site subscene:                {app_config.providers['subscene_site']}")
    output(f"Use site opensubtitles:           {app_config.providers['opensubtitles_site']}")
    output(f"Use hash opensubtitles:           {app_config.providers['opensubtitles_hash']}")
    output(f"Use site yifysubtitles:           {app_config.providers['subscene_site']}")
    output("")
    output_header(f"File data")
    output(f"Filename:                         {__video__.filename}")
    output(f"Directory:                        {__video__.directory_path}")
    output("")
    output_header(f"Release data")
    output(f"Title:                            {release_metadata.title}")
    output(f"Year:                             {release_metadata.year}")
    output(f"Season:                           {release_metadata.season}, {release_metadata.season_ordinal}")
    output(f"Episode:                          {release_metadata.episode}, {release_metadata.episode_ordinal}")
    output(f"Series:                           {release_metadata.tvseries}")
    output(f"Release:                          {release_metadata.release}")
    output(f"Group:                            {release_metadata.group}")
    output(f"File hash:                        {release_metadata.file_hash}")
    output("")
    output_header(f"Provider url data")
    output(f"subscene_site:                    {provider_urls.subscene}")
    output(f"opensubtitles_site:               {provider_urls.opensubtitles}")
    output(f"openSubtitles_hash:               {provider_urls.opensubtitles_hash}")
    output(f"yifysubtitles_site:               {provider_urls.yifysubtitles}")
    output("")


def output_match(provider: str, pct_result: int, key: str, to_log_: bool = False):
    if pct_result >= app_config.percentage_threshold:
        output(f"> {provider:<14}{pct_result:>3}% {key}", to_log=to_log_)
    else:
        output(f"  {provider:<14}{pct_result:>3}% {key}", to_log=to_log_)


def set_logger_data(media: ReleaseMetadata, app: AppConfig, urls: ProviderUrls):
    global release_metadata, app_config, provider_urls
    release_metadata = media
    app_config = app
    provider_urls = urls


def downlod_metadata(provider_: str, formatted_metadata_: list[FormattedMetadata], search_threashold: int):
    output("")
    output(f"--- [Sorted List from {provider_}] ---", False)
    downloaded_printed = False
    not_downloaded_printed = False
    for data in formatted_metadata_:
        if data.pct_result >= search_threashold and not downloaded_printed:
            output(f"--- Has been downloaded ---\n", False)
            downloaded_printed = True
        if data.pct_result <= search_threashold and not not_downloaded_printed:
            output(f"--- Has not been downloaded ---\n", False)
            not_downloaded_printed = True
        output(f"{data.formatted_release}", False)
        output(f"{data.formatted_url}\n", False)
