# main
import time

from src import user_config
from src.tools.current_user import got_key
from src.config import get
from src.tools.log import log_msg
from src.tools.data import get_parameters
from src.tools.os import cwd
from src.subscrape import SearchSubscene
from src.tools.compare import check
from src.tools import file_manager as fm


def main() -> None:
    start = time.perf_counter()
    if got_key() is False:
        user_config.context_menu()
        user_config.select_language()
        return

    scrape = SearchSubscene()
    language: str = get("language")
    languages: list = get("languages")
    for abbr_num, abbr in enumerate(languages):
        abbr_num += 1
        if language in abbr:
            _abbr, language_abbr = abbr.split(", ")
            abbr_supported = True
            break
        elif abbr_num >= len(languages):
            log_msg("[ERROR] Your language is not supported")
            log_msg("[ERROR] Search might be longer for TV-series")
            language_abbr = "en"
            abbr_supported = False

    param = get_parameters(cwd().lower(), language_abbr)

    log_msg("[PARAMETERS]")
    log_msg(f"[LANGUAGE]: {language}, {language_abbr}")
    log_msg(f"[TITLE]: {param.title}")
    log_msg(f"[YEAR]: {param.year}")
    log_msg(f"[SEASON]: {param.season}, {param.season_ordinal}")
    log_msg(f"[EPSISODE]: {param.episode}, {param.episode_ordinal}")
    log_msg(f"[TV-SERIES]: {param.tv_series}")
    log_msg(f"[RELEASE]: {param.release}")
    log_msg(f"[GROUP]: {param.group}")
    log_msg(f"[URL]: {param.url}\n")

    to_be_scraped: list = []
    title_keys = scrape.search_for_title(param.url)
    for key, value in zip(title_keys, title_keys.values()):
        if key.lower() == f"{param.title} ({param.year})":
            log_msg(f"[Movie]: {key} found.")
            log_msg(f"[URL]: {value}")
            to_be_scraped.append(value) if value not in (to_be_scraped) else None
        elif param.title and param.season_ordinal in key.lower() and param.tv_series and abbr_supported:
            log_msg(f"[TV-series]: {key} found.")
            log_msg(f"[URL]: {value}")
            to_be_scraped.append(value) if value not in (to_be_scraped) else None
        elif param.title in key.lower() and param.tv_series and abbr_supported is False:
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

    to_be_downloaded: list = []
    while len(to_be_scraped) > 0:
        for url in to_be_scraped:
            log_msg(f"[Searching for subtitles]")
            sub_keys = scrape.search_title_for_sub(language, url)
            break
        for key, value in zip(sub_keys, sub_keys.values()):
            number = check(key, param.release)
            log_msg(f"[{number.precentage}% match]: {key}") if number.precentage <= 90 else None
            if number.precentage >= 90 or param.title and f"{param.season}{param.episode}" in key.lower() and param.tv_series:
                log_msg(f"[{number.precentage}% match]: {key}")
                log_msg(f"[Appending]: {value}")
                to_be_downloaded.append(value) if value not in to_be_downloaded else None
        to_be_scraped.pop(0) if len(to_be_scraped) > 0 else None
        log_msg("[Done]\n") if len(to_be_downloaded) > 0 else None

    if len(to_be_downloaded) == 0:
        log_msg(f"[subsecen-search]: No subtitles to download for {param.release}")
        elapsed = time.perf_counter() - start
        log_msg(f"[subsecen-search]: Finished in {elapsed} seconds.\n\n")
        return
    log_msg("[Downloading]")
    for enu_num, (dl_url) in enumerate(to_be_downloaded):
        enu_num += 1
        root_dl_url = scrape.get_download_url(dl_url)
        file_path = f"{cwd()}\\{enu_num}.zip"
        log_msg(f"[Downloading]: {enu_num}/{len(to_be_downloaded)}.zip")
        fm.download_zip(file_path, root_dl_url)

    log_msg(f"[Extracting]: .srt's from .zip's")
    fm.extract_zips(cwd(), ".zip")
    log_msg(f"[Re-naming]: Best matching .srt to {param.release}.srt")
    fm.rename_srts(f"{param.release}.srt", cwd(), f"{param.group}.srt", ".srt")
    log_msg(f"[Moving]: Unused .srt's to directory subs/")
    fm.move_files(cwd(), f"{param.group}.srt", ".srt")
    log_msg(f"[Removing] .zip's")
    fm.clean_up(cwd(), ".zip")
    log_msg("[Done]\n")

    elapsed = time.perf_counter() - start
    log_msg(f"[subsecen-search]: Finished in {elapsed} seconds.\n\n")


if __name__ == "__main__":
    main()
