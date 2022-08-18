from typing import Optional

from subsearch.data import __video_directory__
from subsearch.scraper import opensubtitles_soup
from subsearch.utils import log
from subsearch.utils.string_parser import SearchParameters


# decides what to do with all the scrape data
def scrape(param: SearchParameters, lang: str, hi: bool):
    """
    Scrape opensubtitles for subtitles using the given parameters.

    Args:
        param (_type_): url_opensubtitles, file_hash
        lang (str): desired language
        hi (str): if hearing impaired subtitles are desired

    Returns:
        list | None: download links for the subtitle
    """
    to_be_downloaded: Optional[list[str]] = opensubtitles_soup.search_for_hash(param.url_opensubtitles, lang, hi)
    if to_be_downloaded is None:
        if param.show_bool:
            log.output(f"No TV-series found matching hash {param.file_hash}")
        else:
            log.output(f"No movies found matching hash {param.file_hash}")
        return None
    else:
        download_info = []
        log.output(f"Preparing  hash {param.file_hash} for download")
        for current_num, dl_url in enumerate(to_be_downloaded):
            total_num = len(to_be_downloaded)
            current_num += 1
            file_path = f"{__video_directory__}\\opensubtitles_{current_num}.zip"
            x = file_path, dl_url, current_num, total_num
            download_info.append(x)
        log.output(f"Done with tasks")
        return download_info
