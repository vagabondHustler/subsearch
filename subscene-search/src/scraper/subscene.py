from src import log
from src.sos import cwd
from src.scraper.subscene_soup import search_for_title
from src.scraper.subscene_soup import search_title_for_sub
from src.scraper.subscene_soup import get_download_url
from src.compare import check


def scrape(param, language: str, lang_abbr: str, precentage) -> list or None:
    # search for titles
    to_be_scraped: list = []
    title_keys = search_for_title(param.url)
    for key, value in zip(title_keys, title_keys.values()):
        if key.lower() == f"{param.title} ({param.year})":
            log.output(f"Movie {key} found")
            # log.output(f"URL: {value}")
            to_be_scraped.append(value) if value not in (to_be_scraped) else None
        elif param.title and param.season_ordinal in key.lower() and param.tv_series and lang_abbr:
            log.output(f"TV-Series {key} found")
            # log.output(f"URL: {value}")
            to_be_scraped.append(value) if value not in (to_be_scraped) else None
    log.output("Done with task\n") if len(to_be_scraped) > 0 else None

    # exit if no titles found
    if len(to_be_scraped) == 0:
        if param.tv_series:
            log.output(f"No TV-series found matching {param.title}")
        else:
            log.output(f"No movies found matching {param.title}")
        return None

    # search title for subtitles
    to_be_downloaded: list = []
    while len(to_be_scraped) > 0:
        for url in to_be_scraped:
            log.output(f"[Searching for subtitles]")
            sub_keys = search_title_for_sub(language, url)
            break
        for key, value in zip(sub_keys, sub_keys.values()):
            number = check(key, param.release)
            log.output(f"[{number.precentage}% match]: {key}") if number.precentage <= precentage else None
            if number.precentage >= precentage or param.title and f"{param.season}{param.episode}" in key.lower() and param.tv_series:
                log.output(f"[{number.precentage}% match]: {key}")
                # log.output(f"Appending: {value}")
                to_be_downloaded.append(value) if value not in to_be_downloaded else None
        to_be_scraped.pop(0) if len(to_be_scraped) > 0 else None
        log.output("Done with tasks") if len(to_be_downloaded) > 0 else None

    # exit if no subtitles found
    if len(to_be_downloaded) == 0:
        log.output(f"No subtitles to download for {param.release}")
        return None

    download_info: list = []
    for current_num, (dl_url) in enumerate(to_be_downloaded):
        total_num = len(to_be_downloaded)
        current_num += 1
        root_dl_url = get_download_url(dl_url)
        file_path = f"{cwd()}\\{current_num}.zip"
        current_num = (file_path, root_dl_url, current_num, total_num)
        download_info.append(current_num)
    return download_info
