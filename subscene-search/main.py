import time

from src import edit_config
from src.current_user import got_key
from src.config import get
from src.log import log_msg
from src.data import get_parameters
from src.os import cwd
from src.subscrape import search_for_title
from src.subscrape import search_title_for_sub
from src.subscrape import get_download_url
from src.compare import check
from src import file_manager as fm


# TODO: remove logging from main.py and into a separate module


def main() -> None:
    #
    # initialising
    #
    start = time.perf_counter()
    language, lang_abbr = get("language")
    precentage = get("percentage")
    if got_key() is False:
        edit_config.context_menu()
        return exit(0)
    #
    # filter parameters
    #
    param = get_parameters(cwd().lower(), lang_abbr)
    log_msg("[PARAMETERS]")
    log_msg(f"[LANGUAGE]: {language}, {lang_abbr}")
    log_msg(f"[TITLE]: {param.title}")
    log_msg(f"[YEAR]: {param.year}")
    log_msg(f"[SEASON]: {param.season}, {param.season_ordinal}")
    log_msg(f"[EPSISODE]: {param.episode}, {param.episode_ordinal}")
    log_msg(f"[TV-SERIES]: {param.tv_series}")
    log_msg(f"[RELEASE]: {param.release}")
    log_msg(f"[GROUP]: {param.group}")
    log_msg(f"[{precentage}%] Match threshold")
    log_msg(f"[URL]: {param.url}\n")

    #
    # get title
    #
    to_be_scraped: list = []
    title_keys = search_for_title(param.url)
    for key, value in zip(title_keys, title_keys.values()):
        if key.lower() == f"{param.title} ({param.year})":
            log_msg(f"[Movie]: {key} found.")
            log_msg(f"[URL]: {value}")
            to_be_scraped.append(value) if value not in (to_be_scraped) else None
        elif param.title and param.season_ordinal in key.lower() and param.tv_series and lang_abbr:
            log_msg(f"[TV-series]: {key} found.")
            log_msg(f"[URL]: {value}")
            to_be_scraped.append(value) if value not in (to_be_scraped) else None
    log_msg("[Done]\n") if len(to_be_scraped) > 0 else None
    if len(to_be_scraped) == 0:
        if param.tv_series:
            log_msg(f"[subsecen-search]: No TV-series found matching {param.title}.")
        else:
            log_msg(f"[subsecen-search]: No movies found matching {param.title}.")
        elapsed = time.perf_counter() - start
        log_msg(f"[subsecen-search]: Finished in {elapsed} seconds.\n\n")
        return
    #
    # search title for subtitle
    #
    to_be_downloaded: list = []
    while len(to_be_scraped) > 0:
        for url in to_be_scraped:
            log_msg(f"[Searching for subtitles]")
            sub_keys = search_title_for_sub(language, url)
            break
        for key, value in zip(sub_keys, sub_keys.values()):
            number = check(key, param.release)
            log_msg(f"[{number.precentage}% match]: {key}") if number.precentage <= precentage else None
            if number.precentage >= precentage or param.title and f"{param.season}{param.episode}" in key.lower() and param.tv_series:
                log_msg(f"[{number.precentage}% match]: {key}")
                log_msg(f"[Appending]: {value}")
                to_be_downloaded.append(value) if value not in to_be_downloaded else None
        to_be_scraped.pop(0) if len(to_be_scraped) > 0 else None
        log_msg("[Done]\n") if len(to_be_downloaded) > 0 else None
    #
    # check if subtitle is a match, if so download
    #
    if len(to_be_downloaded) == 0:
        log_msg(f"[subsecen-search]: No subtitles to download for {param.release}")
        elapsed = time.perf_counter() - start
        log_msg(f"[subsecen-search]: Finished in {elapsed} seconds.\n\n")
        return
    log_msg("[Downloading]")
    for enu_num, (dl_url) in enumerate(to_be_downloaded):
        enu_num += 1
        root_dl_url = get_download_url(dl_url)
        file_path = f"{cwd()}\\{enu_num}.zip"
        log_msg(f"[Downloading]: {enu_num}/{len(to_be_downloaded)}.zip")
        fm.download_zip(file_path, root_dl_url)
    #
    # extract files, rename files, delete unsued files
    #
    log_msg(f"[Extracting]: .srt's from .zip's")
    fm.extract_zips(cwd(), ".zip")
    log_msg(f"[Re-naming]: Best matching .srt to {param.release}.srt")
    fm.rename_srts(f"{param.release}.srt", cwd(), f"{param.group}.srt", ".srt")
    if len(to_be_downloaded) > 1:
        log_msg(f"[Moving]: Unused .srt's to directory subs/")
        fm.move_files(cwd(), f"{param.group}.srt", ".srt")
    log_msg(f"[Removing] .zip's")
    fm.clean_up(cwd(), ".zip")
    log_msg("[Done]\n")

    elapsed = time.perf_counter() - start
    log_msg(f"[subsecen-search]: Finished in {elapsed} seconds.\n\n")
    focus = get("terminal_focus")
    if focus == "True":
        exit("All done!")


if __name__ == "__main__":
    main()
