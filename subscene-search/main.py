import time


from src import registry
from src.current_user import got_key
from src.config import get
from src import log
from src.data import get_parameters
from src.sos import cwd
from src.subscrape import search_for_title
from src.subscrape import search_title_for_sub
from src.subscrape import get_download_url
from src.compare import check
from src import file_manager as fm


def main() -> None:
    # initialising
    start = time.perf_counter()
    language, lang_abbr = get("language")
    precentage = get("percentage")
    if got_key() is False:
        registry.add_context_menu()
        return exit(0)

    # search parameters
    param = get_parameters(cwd().lower(), lang_abbr)
    log.msg("[PARAMETERS]")
    log.msg(f"Language: {language}, {lang_abbr}")
    log.msg(f"Title: {param.title}")
    log.msg(f"Year: {param.year}")
    log.msg(f"Season: {param.season}, {param.season_ordinal}")
    log.msg(f"Episode: {param.episode}, {param.episode_ordinal}")
    log.msg(f"TV-Series: {param.tv_series}")
    log.msg(f"Release: {param.release}")
    log.msg(f"Group: {param.group}")
    log.msg(f"Match threshold: {precentage}%")
    log.msg(f"URL: {param.url}\n")

    # get title
    to_be_scraped: list = []
    title_keys = search_for_title(param.url)
    for key, value in zip(title_keys, title_keys.values()):
        if key.lower() == f"{param.title} ({param.year})":
            log.msg(f"Movie {key} found.")
            log.msg(f"URL: {value}")
            to_be_scraped.append(value) if value not in (to_be_scraped) else None
        elif param.title and param.season_ordinal in key.lower() and param.tv_series and lang_abbr:
            log.msg(f"TV-Series {key} found.")
            log.msg(f"URL: {value}")
            to_be_scraped.append(value) if value not in (to_be_scraped) else None
    log.msg("Done with task.\n") if len(to_be_scraped) > 0 else None

    # exit if no titles found
    if len(to_be_scraped) == 0:
        if param.tv_series:
            log.msg(f"No TV-series found matching {param.title}.")
        else:
            log.msg(f"No movies found matching {param.title}.")
        elapsed = time.perf_counter() - start
        log.msg(f"Finished in {elapsed} seconds.\n\n")
        return

    # search title for subtitle
    to_be_downloaded: list = []
    while len(to_be_scraped) > 0:
        for url in to_be_scraped:
            log.msg(f"[Searching for subtitles]")
            sub_keys = search_title_for_sub(language, url)
            break
        for key, value in zip(sub_keys, sub_keys.values()):
            number = check(key, param.release)
            log.msg(f"[{number.precentage}% match]: {key}") if number.precentage <= precentage else None
            if number.precentage >= precentage or param.title and f"{param.season}{param.episode}" in key.lower() and param.tv_series:
                log.msg(f"[{number.precentage}% match]: {key}")
                log.msg(f"Appending: {value}")
                to_be_downloaded.append(value) if value not in to_be_downloaded else None
        to_be_scraped.pop(0) if len(to_be_scraped) > 0 else None
        log.msg("Done with tasks.\n") if len(to_be_downloaded) > 0 else None

    # exit if no subtitles found
    if len(to_be_downloaded) == 0:
        log.msg(f"No subtitles to download for {param.release}")
        elapsed = time.perf_counter() - start
        log.msg(f"Finished in {elapsed} seconds.\n\n")
        return

    # check if subtitle is a match, if so download
    log.msg("[Downloading]")
    for current_num, (dl_url) in enumerate(to_be_downloaded):
        total_num = len(to_be_downloaded)
        current_num += 1
        root_dl_url = get_download_url(dl_url)
        file_path = f"{cwd()}\\{current_num}.zip"
        fm.download_zip(file_path, root_dl_url, current_num, total_num)

    # extract files, rename files, delete unused files
    fm.extract_zips(cwd(), ".zip")
    fm.rename_srts(f"{param.release}.srt", cwd(), f"{param.group}.srt", ".srt")
    if len(to_be_downloaded) > 1:
        fm.move_files(cwd(), f"{param.group}.srt", ".srt")
    fm.clean_up(cwd(), ".zip")

    # finnishing up
    elapsed = time.perf_counter() - start
    log.msg("Done with tasks.\n")
    log.msg(f"Finished in {elapsed} seconds.\n\n")


if __name__ == "__main__":
    main()
