from typing import NamedTuple, Optional

from subsearch.data import __video_directory__
from subsearch.scraper import opensubtitles_soup
from subsearch.utils import log
from subsearch.utils.string_parser import SearchParameters


class OpenSubtitlesDownloadData(NamedTuple):
    file_path: str
    url: str
    idx_num: int
    idx_lenght: int


def scrape(param: SearchParameters, lang: str, hi: bool):
    """
    Scrape opensubtitles for subtitles using the given parameters.

    Args:
        param (_type_): url_opensubtitles, file_hash
        lang (str): desired language
        hi (str): if hearing impaired subtitles are desired

    Returns:
        tuple: file_path, dl_url, current_num, total_num
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
        number_of_items = len(to_be_downloaded)
        for current_item_num, dl_url in enumerate(to_be_downloaded, start=1):
            zip_path = f"{__video_directory__}\\__subsearch__opensubtitles_{current_item_num}.zip"
            data = OpenSubtitlesDownloadData(
                file_path=zip_path, url=dl_url, idx_num=current_item_num, idx_lenght=number_of_items
            )
            download_info.append(data)
        log.output(f"Done with tasks")
        return download_info
