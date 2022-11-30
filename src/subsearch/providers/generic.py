import cloudscraper
from selectolax.parser import HTMLParser

from subsearch.data.data_fields import (
    DownloadData,
    FormattedData,
    ProviderUrlData,
    ReleaseData,
    UserData,
)
from subsearch.utils import log

class BaseProvider:
    """
    Base class for providers
    """

    def __init__(self, rd: ReleaseData, ud: UserData, pud: ProviderUrlData):
        self.release_data = rd
        self.user_data = ud
        self.provider_data = pud

        # file parameters
        self.title = rd.title
        self.year = rd.year
        self.season = rd.season
        self.season_ordinal = rd.season_ordinal
        self.episode = rd.episode
        self.episode_ordinal = rd.episode_ordinal
        self.series = rd.series
        self.release = rd.release
        self.group = rd.group
        self.file_hash = rd.file_hash
        # user parameters
        self.current_language = ud.current_language
        self.hi_sub = ud.hearing_impaired
        self.non_hi_sub = ud.non_hearing_impaired
        self.pct_threashold = ud.percentage
        self.show_download_window = ud.show_download_window
        # provider url data
        self.url_subscene = pud.subscene
        self.url_opensubtitles = pud.opensubtitles
        self.url_opensubtitles_hash = pud.opensubtitles_hash
        self.url_yifysubtitles = pud.yifysubtitles

    def is_threshold_met(self, key: str, pct_result: int) -> bool:
            if pct_result >= self.pct_threashold or self.title and f"{self.season}{self.episode}" in key.lower() and self.series:
                return True
            return False

def get_html(url: str):
    scraper = cloudscraper.create_scraper(browser={"browser": "chrome", "platform": "android", "desktop": False})
    response = scraper.get(url)
    return HTMLParser(response.text)


def pack_download_data(_provider: str, video_tmp_directory: str, to_be_downloaded: dict[str, str]) -> list[DownloadData]:
    download_info = []
    tbd_lenght = len(to_be_downloaded)
    for zip_idx, (zip_name, zip_url) in enumerate(to_be_downloaded.items(), start=1):
        zip_fp = f"{video_tmp_directory}\\{_provider}_{zip_idx}.zip"
        data = DownloadData(
            provider=_provider, name=zip_name, file_path=zip_fp, url=zip_url, idx_num=zip_idx, idx_lenght=tbd_lenght
        )
        download_info.append(data)
    return download_info


def format_key_value_pct(_provider: str, key: str, value: str, _pct_result: int) -> FormattedData:
    lenght_str = sum(1 for char in f"{_pct_result:>3}% match:")
    number_of_spaces = " " * lenght_str
    _match_release = f"{_pct_result:>3}% match: {key}"
    _url = f"{number_of_spaces} {value}"
    data = FormattedData(
        provider=_provider,
        release=key,
        url=value,
        pct_result=_pct_result,
        formatted_release=_match_release,
        formatted_url=_url,
    )
    return data


def log_and_sort_list(_provider: str, _list: list[FormattedData], pct: int) -> list[FormattedData]:
    _list.sort(key=lambda x: x.pct_result, reverse=True)
    log.output("")
    log.output(f"--- [Sorted List from {_provider}] ---", False)
    hbd_printed = False
    hnbd_printed = False
    for data in _list:
        if data.pct_result >= pct and not hbd_printed:
            log.output(f"--- Has been downloaded ---\n", False)
            hbd_printed = True
        if data.pct_result <= pct and not hnbd_printed:
            log.output(f"--- Has not been downloaded ---\n", False)
            hnbd_printed = True
        log.output(f"{data.formatted_release}", False)
        log.output(f"{data.formatted_url}\n", False)
    return _list
