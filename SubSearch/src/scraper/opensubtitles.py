from src import log
from src.sos import cwd
from src.scraper.opensubtitles_soup import search_for_hash

# decides what to do with all the scrape data
def scrape(parameters, language: str, hearing_impaired: str) -> list or None:
    # search for titles
    to_be_downloaded = search_for_hash(parameters.url_opensubtitles, language, hearing_impaired)
    if to_be_downloaded is None:
        if parameters.tv_series:
            log.output(f"No TV-series found matching hash {parameters.file_hash}")
        else:
            log.output(f"No movies found matching hash {parameters.file_hash}")
        return None

    download_info: list = []
    for current_num, (dl_url) in enumerate(to_be_downloaded):
        total_num = len(to_be_downloaded)
        current_num += 1
        file_path = f"{cwd()}\\opensubtitles_{current_num}.zip"
        current_num = (file_path, dl_url, current_num, total_num)
        download_info.append(current_num)
    return download_info

    # for key, value in title_keys.items():
    #     if is_movie(key, parameters):
    #         to_be_scraped.append(value) if value not in (to_be_scraped) else None
    #     if is_tv_series(key, lang_abbr, parameters):
    #         to_be_scraped.append(value) if value not in (to_be_scraped) else None
    # log.output("Done with task\n") if len(to_be_scraped) > 0 else None

    # # exit if no titles found
    # if len(to_be_scraped) == 0:
    #     if parameters.tv_series:
    #         log.output(f"No TV-series found matching {parameters.title}")
    #     else:
    #         log.output(f"No movies found matching {parameters.title}")
    #     return None

    # # search title for subtitles
    # to_be_downloaded: list = []
    # while len(to_be_scraped) > 0:
    #     for url in to_be_scraped:
    #         log.output(f"[Searching for subtitles]")
    #         sub_keys = search_title_for_sub(lang_abbr, url)
    #         break
    #     for key, value in sub_keys.items():
    #         number = check(key, parameters.release)
    #         log.output(f"[{number.precentage}% match]: {key}") if number.precentage <= precentage else None
    #         if is_threshold(key, number, precentage, parameters):
    #             to_be_downloaded.append(value) if value not in to_be_downloaded else None
    #     to_be_scraped.pop(0) if len(to_be_scraped) > 0 else None
    #     log.output("Done with tasks") if len(to_be_downloaded) > 0 else None

    # # exit if no subtitles found
    # if len(to_be_downloaded) == 0:
    #     log.output(f"No subtitles to download for {parameters.release}")
    #     return None
