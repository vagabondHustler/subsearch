import logging
from datetime import datetime

from data import __version__

NOW = datetime.now()
DATE = NOW.strftime("%y%m%d")


logging.basicConfig(
    filename=f"__subsearch__.log",
    filemode="w",
    level=logging.DEBUG,
    format="%(asctime)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
)

# log and print message
def output(msg: str, print_to_terminal: bool = True) -> None:
    logging.info(msg)
    print(msg) if print_to_terminal else False


# log and print all the used parameters from video/directory-name
def parameters(param: str, language: str, lang_abbr: str, hearing_impaired: str, percentage: int) -> None:
    output(f"SubSearch - {__version__} ", False)
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
