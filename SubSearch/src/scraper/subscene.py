from src.utilities.local_paths import cwd
from src.scraper.subscene_soup import get_download_url, search_for_title, search_title_for_sub
from src.utilities import log
from src.utilities.compare import check


# check if dict is of movies
def is_movie(key: str, p=None) -> bool:
    if key.lower() == f"{p.title} ({p.year})":
        log.output(f"Movie {key} found")
        return True
    return False


# check if the movie might have been released the year before
def try_the_year_before(key: str, p=None) -> bool:
    if p.year == "N/A":
        return False
    year = int(p.year) - 1
    the_year_before = f"{p.title} ({year})"
    if key.lower().startswith(the_year_before):
        log.output(f"Movie {key} found")
        return True


# check if dict is of tv-series
def is_tv_series(key: str, lang_abbr: str, p=None) -> bool:
    if p.title and p.season_ordinal in key.lower() and p.tv_series and lang_abbr:
        log.output(f"TV-Series {key} found")
        return True
    return False


# check str is above precentage threshold
def is_threshold(key: str, number: int, pct: int, p=None) -> bool:
    if (
        number.precentage >= pct
        or p.title
        and f"{p.season}{p.episode}" in key.lower()
        and p.tv_series
    ):
        return True
    return False


# log and sort list
def log_and_sort_list(list_of_tuples: list, precentage) -> list:
    list_of_tuples.sort(key=lambda x: x[0], reverse=True)
    log.output("\n[Sorted List from Subscene]")
    hbd_printed = False
    hnbd_printed = False
    for i in list_of_tuples:
        name = i[1]
        url = i[2]
        if i[0] >= precentage and not hbd_printed:
            log.output(f"--- Has been downloaded ---\n")
            hbd_printed = True
        if i[0] <= precentage and not hnbd_printed:
            log.output(f"--- Has not been downloaded ---\n")
            hnbd_printed = True
        log.output(f"{name}\n{url}\n")
    return list_of_tuples


# decides what to do with all the scrape data
def scrape(
    parameters, language: str, lang_abbr: str, hearing_impaired: str, precentage
) -> list or None:
    # search for titles
    to_be_scraped: list = []
    title_keys = search_for_title(parameters.url_subscene)
    if title_keys == "ERROR: CAPTCHA PROTECTION":
        log.output(f"Captcha protection detected. Please try again later.")
        return None
    for key, value in title_keys.items():
        if is_movie(key, parameters):
            to_be_scraped.append(value) if value not in (to_be_scraped) else None
        if try_the_year_before(key, parameters):
            to_be_scraped.append(value) if value not in (to_be_scraped) else None
        if is_tv_series(key, lang_abbr, parameters):
            to_be_scraped.append(value) if value not in (to_be_scraped) else None
    log.output("Done with task\n") if len(to_be_scraped) > 0 else None

    # exit if no titles found
    if len(to_be_scraped) == 0:
        if parameters.tv_series:
            log.output("")
            log.output(f"No TV-series found matching {parameters.title}")
        else:
            log.output("")
            log.output(f"No movies found matching {parameters.title}")
        return None

    # search title for subtitles
    to_be_downloaded: list = []
    to_be_sorted: list = []
    while len(to_be_scraped) > 0:
        for url in to_be_scraped:
            log.output(f"[Searching for subtitles]")
            sub_keys = search_title_for_sub(language, hearing_impaired, url)
            break
        for key, value in sub_keys.items():
            number = check(key, parameters.release)
            log.output(f"[Found]: {key}")
            lenght_str = sum(1 for char in f"[{number.precentage}% match]:")
            formatting_spaces = " " * lenght_str
            _name = f"[{number.precentage}% match]: {key}"
            _url = f"{formatting_spaces} {value}"
            to_be_sorted_value = number.precentage, _name, _url
            to_be_sorted.append(to_be_sorted_value)
            if is_threshold(key, number, precentage, parameters):
                to_be_downloaded.append(value) if value not in to_be_downloaded else None
        to_be_scraped.pop(0) if len(to_be_scraped) > 0 else None
        log_and_sort_list(to_be_sorted, precentage)
        log.output("Done with tasks")

    # exit if no subtitles found
    if len(to_be_downloaded) == 0:
        log.output("")
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
