from utils import local_paths, log, string_parser

from . import subscene_soup


# check if dict is of movies
def is_movie(key: str, param=None) -> bool:
    if key.lower() == f"{param.title} ({param.year})":
        log.output(f"Movie {key} found")
        return True
    return False


# check if the movie might have been released the year before
def try_the_year_before(key: str, param=None) -> bool:
    if param.year == "N/A":
        return False
    year = int(param.year) - 1
    the_year_before = f"{param.title} ({year})"
    if key.lower().startswith(the_year_before):
        log.output(f"Movie {key} found")
        return True


# check if dict is of tv-series
def is_tv_series(key: str, lang_abbr: str, param=None) -> bool:
    if param.title and param.season_ordinal in key.lower() and param.tv_series and lang_abbr:
        log.output(f"TV-Series {key} found")
        return True
    return False


# check str is above percentage threshold
def is_threshold(key: str, number: int, pct: int, param=None) -> bool:
    if number.percentage >= pct or param.title and f"{param.season}{param.episode}" in key.lower() and param.tv_series:
        return True
    return False


# log and sort list
def log_and_sort_list(list_of_tuples: list, pct: int) -> list:
    list_of_tuples.sort(key=lambda x: x[0], reverse=True)
    log.output("\n[Sorted List from Subscene]")
    hbd_printed = False
    hnbd_printed = False
    for i in list_of_tuples:
        name = i[1]
        url = i[2]
        if i[0] >= pct and not hbd_printed:
            log.output(f"--- Has been downloaded ---\n")
            hbd_printed = True
        if i[0] <= pct and not hnbd_printed:
            log.output(f"--- Has not been downloaded ---\n")
            hnbd_printed = True
        log.output(f"{name}\n{url}\n")
    return list_of_tuples


# decides what to do with all the scrape data
def scrape(param, lang: str, lang_abbr: str, hi: str, pct: int, show_dl_window: str) -> list | None:
    # search for titles
    to_be_scraped: list = []
    title_keys = subscene_soup.search_for_title(param.url_subscene)
    if title_keys == "ERROR: CAPTCHA PROTECTION":
        log.output(f"Captcha protection detected. Please try again later.")
        return None
    for key, value in title_keys.items():
        if is_movie(key, param):
            to_be_scraped.append(value) if value not in (to_be_scraped) else None
        if try_the_year_before(key, param):
            to_be_scraped.append(value) if value not in (to_be_scraped) else None
        if is_tv_series(key, lang_abbr, param):
            to_be_scraped.append(value) if value not in (to_be_scraped) else None
    log.output("Done with task\n") if len(to_be_scraped) > 0 else None

    # exit if no titles found
    if len(to_be_scraped) == 0:
        if param.tv_series:
            log.output("")
            log.output(f"No TV-series found matching {param.title}")
        else:
            log.output("")
            log.output(f"No movies found matching {param.title}")
        return None

    # search title for subtitles
    to_be_downloaded: list = []
    to_be_sorted: list = []
    while len(to_be_scraped) > 0:
        for url in to_be_scraped:
            log.output(f"[Searching for subtitles]")
            sub_keys = subscene_soup.search_title_for_sub(lang, hi, url)
            break
        for key, value in sub_keys.items():
            number = string_parser.pct_value(key, param.release)
            log.output(f"[Found]: {key}")
            lenght_str = sum(1 for char in f"[{number.percentage}% match]:")
            formatting_spaces = " " * lenght_str
            _name = f"[{number.percentage}% match]: {key}"
            _url = f"{formatting_spaces} {value}"
            to_be_sorted_value = number.percentage, _name, _url
            to_be_sorted.append(to_be_sorted_value)
            if is_threshold(key, number, pct, param):
                to_be_downloaded.append(value) if value not in to_be_downloaded else None
        to_be_scraped.pop(0) if len(to_be_scraped) > 0 else None
        sorted_list = log_and_sort_list(to_be_sorted, pct)
        log.output("Done with tasks")

    # exit if no subtitles found
    if len(to_be_downloaded) == 0:
        log.output("")
        log.output(f"No subtitles to download for {param.release}")
        if show_dl_window and len(sorted_list) > 0:
            with open("__subsearch__dl_data.tmp", "w", encoding="utf8") as f:
                for i in range(len(sorted_list)):
                    name, _link = sorted_list[i][1], sorted_list[i][2]
                    link = _link.replace(" ", "")
                    f.writelines(f"{name} {link}")
                    f.write("\n")

            return None
        return None

    download_info: list = []
    for current_num, (dl_url) in enumerate(to_be_downloaded):
        total_num = len(to_be_downloaded)
        current_num += 1
        root_dl_url = subscene_soup.get_download_url(dl_url)
        file_path = f"{local_paths.cwd()}\\__subsearch__subscene_{current_num}.zip"
        current_num = (file_path, root_dl_url, current_num, total_num)
        download_info.append(current_num)
    return download_info
