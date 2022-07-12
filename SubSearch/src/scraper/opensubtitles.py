from src.utilities import log
from src.local_paths import cwd
from src.scraper.opensubtitles_soup import search_for_hash


# decides what to do with all the scrape data
def scrape(parameters, language: str, hearing_impaired: str) -> list or None:
    to_be_downloaded = search_for_hash(parameters.url_opensubtitles, language, hearing_impaired)
    if to_be_downloaded is None:
        if parameters.tv_series:
            log.output(f"No TV-series found matching hash {parameters.file_hash}")
        else:
            log.output(f"No movies found matching hash {parameters.file_hash}")
        return None

    download_info: list = []
    log.output(f"Preparing  hash {parameters.file_hash} for download")
    for current_num, (dl_url) in enumerate(to_be_downloaded):
        total_num = len(to_be_downloaded)
        current_num += 1
        file_path = f"{cwd()}\\opensubtitles_{current_num}.zip"
        current_num = (file_path, dl_url, current_num, total_num)
        download_info.append(current_num)
    log.output(f"Done with tasks")
    return download_info
