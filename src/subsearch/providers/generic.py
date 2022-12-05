import cloudscraper
from selectolax.parser import HTMLParser

from subsearch.data.data_objects import (
    AppConfig,
    DownloadMetaData,
    FormattedMetadata,
    MediaMetadata,
    ProviderUrls,
)
from subsearch.utils import log


class ProviderParameters:
    """
    Parameters for provider
    """

    def __init__(self, media: MediaMetadata, app: AppConfig, urls: ProviderUrls):
        self.release_data = media
        self.user_data = app
        self.provider_data = urls

        # file parameters
        self.title = media.title
        self.year = media.year
        self.season = media.season
        self.season_ordinal = media.season_ordinal
        self.episode = media.episode
        self.episode_ordinal = media.episode_ordinal
        self.series = media.tvseries
        self.release = media.release
        self.group = media.group
        self.file_hash = media.file_hash
        # user parameters
        self.current_language = app.current_language
        self.hi_sub = app.hearing_impaired
        self.non_hi_sub = app.non_hearing_impaired
        self.percentage_threashold = app.percentage_threshold
        self.manual_download_tab = app.manual_download_tab
        # provider url data
        self.url_subscene = urls.subscene
        self.url_opensubtitles = urls.opensubtitles
        self.url_opensubtitles_hash = urls.opensubtitles_hash
        self.url_yifysubtitles = urls.yifysubtitles

    def is_threshold_met(self, key: str, pct_result: int) -> bool:
        if (
            pct_result >= self.percentage_threashold
            or self.title
            and f"{self.season}{self.episode}" in key.lower()
            and self.series
        ):
            return True
        return False


def get_cloudscraper():
    return cloudscraper.create_scraper(browser={"browser": "chrome", "platform": "android", "desktop": False})


def get_html_parser(url: str):
    scraper = get_cloudscraper()
    response = scraper.get(url)
    return HTMLParser(response.text)


def pack_download_data(provider_: str, video_tmp_directory: str, to_be_downloaded: dict[str, str]) -> list[DownloadMetaData]:
    download_info = []
    tbd_lenght = len(to_be_downloaded)
    for zip_idx, (zip_name, zip_url) in enumerate(to_be_downloaded.items(), start=1):
        zip_fp = f"{video_tmp_directory}\\{provider_}_{zip_idx}.zip"
        data = DownloadMetaData(
            provider=provider_, name=zip_name, file_path=zip_fp, url=zip_url, idx_num=zip_idx, idx_lenght=tbd_lenght
        )
        download_info.append(data)
    return download_info


def format_key_value_pct(provider_: str, key: str, value: str, precentage_result_: int) -> FormattedMetadata:
    lenght_str = sum(1 for char in f"{precentage_result_:>3}% match:")
    number_of_spaces = " " * lenght_str
    _match_release = f"{precentage_result_:>3}% match: {key}"
    _url = f"{number_of_spaces} {value}"
    data = FormattedMetadata(
        provider=provider_,
        release=key,
        url=value,
        pct_result=precentage_result_,
        formatted_release=_match_release,
        formatted_url=_url,
    )
    return data


def log_and_sort_list(provider_: str, list_: list[FormattedMetadata], precentage: int) -> list[FormattedMetadata]:
    list_.sort(key=lambda x: x.pct_result, reverse=True)
    log.output("")
    log.output(f"--- [Sorted List from {provider_}] ---", False)
    downloaded_printed = False
    not_downloaded_printed = False
    for data in list_:
        if data.pct_result >= precentage and not downloaded_printed:
            log.output(f"--- Has been downloaded ---\n", False)
            downloaded_printed = True
        if data.pct_result <= precentage and not not_downloaded_printed:
            log.output(f"--- Has not been downloaded ---\n", False)
            not_downloaded_printed = True
        log.output(f"{data.formatted_release}", False)
        log.output(f"{data.formatted_url}\n", False)
    return list_
