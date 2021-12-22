from src import log
from src.sos import cwd
from src.scraper.subscene_soup import search_for_title
from src.scraper.subscene_soup import search_title_for_sub
from src.scraper.subscene_soup import get_download_url
from src.compare import check

# check if dict is of movies
def is_movie(key: str, p=None) -> bool:
    if key.lower() == f"{p.title} ({p.year})":
        log.output(f"Movie {key} found")
        return True
    return False


# check if dict is of tv-series
def is_tv_series(key: str, lang_abbr: str, p=None) -> bool:
    if p.title and p.season_ordinal in key.lower() and p.tv_series and lang_abbr:
        log.output(f"TV-Series {key} found")
        return True
    return False


# check str is above precentage threshold
def is_threshold(key: str, number: int, pct: int, p=None) -> bool:
    if number.precentage >= pct or p.title and f"{p.season}{p.episode}" in key.lower() and p.tv_series:
        log.output(f"[{number.precentage}% match]: {key}")
        return True
    return False


# decides what to do with all the scrape data
def scrape(parameters, language: str, lang_abbr: str, hearing_impaired: str, precentage) -> list or None:
    # search for titles
    to_be_scraped: list = []
    title_keys = search_for_title(parameters.url_subscene)
    for key, value in title_keys.items():
        if is_movie(key, parameters):
            to_be_scraped.append(value) if value not in (to_be_scraped) else None
        if is_tv_series(key, lang_abbr, parameters):
            to_be_scraped.append(value) if value not in (to_be_scraped) else None
    log.output("Done with task\n") if len(to_be_scraped) > 0 else None

    # exit if no titles found
    if len(to_be_scraped) == 0:
        if parameters.tv_series:
            log.output(f"No TV-series found matching {parameters.title}")
        else:
            log.output(f"No movies found matching {parameters.title}")
        return None

    # search title for subtitles
    to_be_downloaded: list = []
    while len(to_be_scraped) > 0:
        for url in to_be_scraped:
            log.output(f"[Searching for subtitles]")
            sub_keys = search_title_for_sub(language, hearing_impaired, url)
            break
        for key, value in sub_keys.items():
            number = check(key, parameters.release)
            log.output(f"[{number.precentage}% match]: {key}") if number.precentage <= precentage else None
            if is_threshold(key, number, precentage, parameters):
                to_be_downloaded.append(value) if value not in to_be_downloaded else None
        to_be_scraped.pop(0) if len(to_be_scraped) > 0 else None
        log.output("Done with tasks") if len(to_be_downloaded) > 0 else None

    # exit if no subtitles found
    if len(to_be_downloaded) == 0:
        print("\n")
        log.output(f"No subtitles to download for {parameters.release}")
        return None

    download_info: list = []
    for current_num, (dl_url) in enumerate(to_be_downloaded):
        total_num = len(to_be_downloaded)
        current_num += 1
        root_dl_url = get_download_url(dl_url)
        file_path = f"{cwd()}\\subscene_{current_num}.zip"
        current_num = (file_path, root_dl_url, current_num, total_num)
        download_info.append(current_num)
    return download_info
