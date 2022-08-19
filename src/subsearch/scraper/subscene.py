from subsearch.data import __video_directory__
from subsearch.scraper import subscene_soup
from subsearch.utils import log, string_parser
from subsearch.utils.string_parser import SearchParameters


# check if dict is of movies
def is_movie(key: str, param: SearchParameters) -> bool:
    """
    Check if key is a movie, by checking if the title is followed by a year. Title.Of.The.Movie.YEAR.Source.Codec-GROUP

    Args:
        key (str): name of the file plus release information
        param (SearchParameters, optional): title, year. Defaults to None.

    Returns:
        bool: True if title is followed by a year, False otherwise
    """
    if key.lower() == f"{param.title} ({param.year})":
        log.output(f"Movie {key} found")
        return True
    return False


# check if the movie might have been released the year before
def try_the_year_before(key: str, param: SearchParameters) -> bool:
    """
    Some releases are released close to the next year. If so, the year might differ from the year in the title.
    This function subtracts one year from the year in the title and checks if the release is in the list.

    Args:
        key (str): name of the file plus release information
        param (SearchParameters, optional): title, year. Defaults to None.

    Returns:
        bool: True if the release is found one year before, False otherwise
    """
    if param.year == "N/A":
        return False
    year = int(param.year) - 1
    the_year_before = f"{param.title} ({year})"
    if key.lower().startswith(the_year_before):
        log.output(f"Movie {key} found")
        return True
    return False


# check if dict is of tv-series
def is_show_bool(key: str, lang_code2: str, param: SearchParameters) -> bool:
    """
    Check if key is a movie, by checking if the title is followed by a SeasonEpisode. Title.Of.The.S00E00.Source.Codec-GROUP

    Args:
        key (str): name of the file plus release information
        lang_abbr (str): language abbreviation for ordinal numbers
        param (SearchParameters, optional): title, season_ordinal, show_bool. Defaults to None.

    Returns:
        bool: True if title is followed by a SeasonEpisode, False otherwise
    """
    if param.title and param.season_ordinal in key.lower() and param.show_bool and lang_code2:
        log.output(f"TV-Series {key} found")
        return True
    return False


# check str is above percentage threshold
def is_threshold(key: str, number: int, pct: int, param: SearchParameters) -> bool:
    """
    Check if the title and release information is equal or above the percentage threshold.

    Args:
        key (str): name of the file plus release information
        number (int): percentage threshold
        pct (int): actual percentage
        param (_type_, optional): title, season, episode, show_bool. Defaults to None.

    Returns:
        bool: True if the percentage is equal or above the threshold, False otherwise
    """
    if number >= pct or param.title and f"{param.season}{param.episode}" in key.lower() and param.show_bool:
        return True
    return False


# log and sort list
def log_and_sort_list(list_of_tuples: list[tuple[int, str, str]], pct: int):
    """
    Log all the result and sort the list from highest to lowest percentage.

    Args:
        list_of_tuples (list): name of the file plus release information
        pct (int): matching percentage

    Returns:
        list: sorted list of tuples(release, url)
    """
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
def scrape(param: SearchParameters, lang: str, lang_abbr: str, hi: str, pct: int, show_dl_window: str):
    # search for titles
    to_be_scraped: list[str] = []
    title_keys = subscene_soup.search_for_title(param.url_subscene)
    if title_keys == "ERROR: CAPTCHA PROTECTION":
        log.output(f"Captcha protection detected. Please try again later.")
        return None
    for key, value in title_keys.items():
        if is_movie(key, param):
            to_be_scraped.append(value) if value not in (to_be_scraped) else None
        if try_the_year_before(key, param):
            to_be_scraped.append(value) if value not in (to_be_scraped) else None
        if is_show_bool(key, lang_abbr, param):
            to_be_scraped.append(value) if value not in (to_be_scraped) else None
    log.output("Done with task\n") if len(to_be_scraped) > 0 else None

    # exit if no titles found
    if len(to_be_scraped) == 0:
        if param.show_bool:
            log.output("")
            log.output(f"No TV-series found matching {param.title}")
        else:
            log.output("")
            log.output(f"No movies found matching {param.title}")
        return None

    # search title for subtitles
    to_be_downloaded: list[str] = []
    to_be_sorted: list[tuple[int, str, str]] = []
    while len(to_be_scraped) > 0:
        for url in to_be_scraped:
            log.output(f"[Searching for subtitles]")
            sub_keys = subscene_soup.search_title_for_sub(lang, hi, url)
            break
        for key, value in sub_keys.items():
            number = string_parser.get_pct_value(key, param.release)
            log.output(f"[Found]: {key}")
            lenght_str = sum(1 for char in f"[{number}% match]:")
            formatting_spaces = " " * lenght_str
            _name = f"[{number}% match]: {key}"
            _url = f"{formatting_spaces} {value}"
            to_be_sorted_value = number, _name, _url
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
            file = f"{__video_directory__}\\__subsearch__dl_data.tmp"
            with open(file, "w", encoding="utf8") as f:
                for i in range(len(sorted_list)):
                    name, _link = sorted_list[i][1], sorted_list[i][2]
                    link = _link.replace(" ", "")
                    f.writelines(f"{name} {link}")
                    f.write("\n")

            return None
        return None

    download_info: list[tuple[str, str, int, int]] = []
    for current_num, (dl_url) in enumerate(to_be_downloaded):
        total_num = len(to_be_downloaded)
        current_num += 1
        root_dl_url = subscene_soup.get_download_url(dl_url)
        file_path = f"{__video_directory__}\\__subsearch__subscene_{current_num}.zip"
        items = (file_path, root_dl_url, current_num, total_num)
        download_info.append(items)
    return download_info
