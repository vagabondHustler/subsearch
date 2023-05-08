import logging
import warnings
from datetime import datetime
from pathlib import Path
from threading import Lock

from subsearch.data import __version__, video_data
from subsearch.data.data_objects import (
    AppConfig,
    FormattedMetadata,
    LanguageData,
    ProviderUrls,
    ReleaseData,
)
from subsearch.utils import io_json

NOW = datetime.now()
DATE = NOW.strftime("%y%m%d")
LOG_TO_FILE = io_json.get_json_key("log_to_file")


logger = logging.getLogger("subsearch")
logger.setLevel(logging.DEBUG)

release_data: ReleaseData
app_config: AppConfig
provider_urls: ProviderUrls
language_data: LanguageData

if video_data is not None and LOG_TO_FILE:
    warnings.filterwarnings("ignore", lineno=545)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", datefmt="%d-%b-%y %H:%M:%S")
    file_handler = logging.FileHandler(Path(video_data.directory_path) / "subsearch.log", "w")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


def output(msg: str, terminal: bool = True, to_log: bool = True, level: str = "info"):
    def _to_log(msg: str, level: str) -> None:
        if video_data is None or LOG_TO_FILE is False:
            return
        if to_log is False:
            return
        log_methods = {
            "info": logger.info,
            "warning": logger.warning,
            "error": logger.error,
            "critical": logger.critical,
        }
        log_methods[level](msg)

    def _to_terminal(msg: str, to_terminal, level: str) -> None:
        if to_terminal is False:
            return
        if level == "info":
            lock = Lock()
            lock.acquire()
            print(msg)
            lock.release()
        else:
            print(f"{level.upper()} - {msg}")

    _to_log(msg, level)
    _to_terminal(msg, terminal, level)


def warning_spaces_in_filename() -> None:
    name_unresolved = f"{video_data.filename}{video_data.file_extension}"
    output(f"File: '{name_unresolved}' contains spaces", level="warning")
    output(f"Results may vary, use punctuation marks for a more accurate result", level="info")
    output("")


def output_header(msg: str) -> None:
    output(f"--- [{msg}] ---")


def output_skip_provider(provider: str, reason: str) -> None:
    output("")
    output_header(f"Skipping {provider}")
    output(f"{reason}")
    output("Done with tasks")
    output("")


def output_done_with_tasks(end_new_line: bool = False) -> None:
    output("Done with tasks")
    if end_new_line:
        output("")


def output_parameters() -> None:
    """
    Logs the parameters used by the application.

    Args:
        data: A dictionary containing the header and the data.

    Returns:
        None
    """
    data = {
        "User data": [
            {"Language": f"{language_data.name}, {language_data.alpha_1}, {language_data.alpha_2b}"},
            {"Use HI subtitle": app_config.hearing_impaired},
            {"Use non-HI subtitle": app_config.non_hearing_impaired},
            {"Match threshold": f"{app_config.percentage_threshold}%"},
            {"Use site subscene": app_config.providers["subscene_site"]},
            {"Use site opensubtitles": app_config.providers["opensubtitles_site"]},
            {"Use hash opensubtitles": app_config.providers["opensubtitles_hash"]},
            {"Use site yifysubtitles": app_config.providers["yifysubtitles_site"]},
        ],
        "File data": [{"Filename": video_data.filename}, {"Directory": video_data.directory_path}],
        "Release data": [
            {"Title": release_data.title},
            {"Year": release_data.year},
            {"Season": f"{release_data.season}, {release_data.season_ordinal}"},
            {"Episode": f"{release_data.episode}, {release_data.episode_ordinal}"},
            {"Series": release_data.tvseries},
            {"Release": release_data.release},
            {"Group": release_data.group},
            {"File hash": release_data.file_hash},
        ],
        "Provider url data": [
            {"subscene_site": provider_urls.subscene},
            {"opensubtitles_site": provider_urls.opensubtitles},
            {"opensubtitles_hash": provider_urls.opensubtitles_hash},
            {"yifysubtitles_site": provider_urls.yifysubtitles},
        ],
    }
    for header, header_data in data.items():
        output_header(header)
        for item in header_data:
            key, value = list(item.items())[0]
            padding = " " * (30 - len(key))
            output(f"{key}:{padding}{value}")
        output("")


def output_match(provider: str, pct_result: int, key: str, to_log_: bool = False) -> None:
    if pct_result >= app_config.percentage_threshold:
        output(f"> {provider:<14}{pct_result:>3}% {key}", to_log=to_log_)
    else:
        output(f"  {provider:<14}{pct_result:>3}% {key}", to_log=to_log_)


def path_action(action_type: str, src_: Path, dst_: Path | None = None) -> None:
    """
    Logs a message indicating the removal, renaming, moving, or extraction of a file or directory.

    Args:
        action_type (str): A string representing the type of action being performed (e.g. "remove", "rename", "move", "extract").
        src_ (Path): A Path object representing the file or directory being acted upon.
        dst_ (Path, optional): An optional Path object representing the new location or name of the file or directory (used for renaming, moving and extracting actions). Defaults to None.

    Returns:
        None
    """
    if src_.is_file():
        type = "file"
    elif src_.is_dir():
        type = "directory"

    src = src_.relative_to(src_.parent.parent) if src_ else None
    dst = dst_.relative_to(dst_.parent.parent) if dst_ else None

    action_messages: dict[str, str] = {
        "remove": rf"Removing {type}: ...\{src}",
        "rename": rf"Renaming {type}: ...\{src} -> ...\{dst}",
        "move": rf"Moving {type}: ...\{src} -> ...\{dst}",
        "extract": rf"Extracting archive: ...\{src} -> ...\{dst}",
    }

    message = action_messages.get(action_type)

    if not message:
        raise ValueError("Invalid action type")

    output(message)


def set_logger_data(**kwargs) -> None:
    global release_data, app_config, provider_urls, language_data
    release_data = kwargs["release_data"]
    app_config = kwargs["app_config"]
    provider_urls = kwargs["provider_urls"]
    language_data = kwargs["language_data"]


def downlod_metadata(provider_: str, formatted_metadata_: list[FormattedMetadata], search_threashold: int) -> None:
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
