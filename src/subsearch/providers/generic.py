import cloudscraper
from selectolax.parser import HTMLParser

from subsearch.data.data_objects import (
    AppConfig,
    DownloadMetaData,
    FormattedMetadata,
    ProviderUrls,
    ReleaseMetadata,
)
from subsearch.utils import log


class ProviderParameters:
    """
    Parameters for provider
    """

    def __init__(self, release_metadata: ReleaseMetadata, app_config: AppConfig, urls: ProviderUrls):
        self.release_data = release_metadata
        self.user_data = app_config
        self.provider_data = urls

        # file parameters
        self.title = release_metadata.title
        self.year = release_metadata.year
        self.season = release_metadata.season
        self.season_ordinal = release_metadata.season_ordinal
        self.episode = release_metadata.episode
        self.episode_ordinal = release_metadata.episode_ordinal
        self.series = release_metadata.tvseries
        self.release = release_metadata.release
        self.group = release_metadata.group
        self.file_hash = release_metadata.file_hash
        # user parameters
        self.current_language = app_config.current_language
        self.hi_sub = app_config.hearing_impaired
        self.non_hi_sub = app_config.non_hearing_impaired
        self.percentage_threashold = app_config.percentage_threshold
        self.manual_download_tab = app_config.manual_download_tab
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


def sort_download_metadata(list_: list[FormattedMetadata]) -> list[FormattedMetadata]:
    list_.sort(key=lambda x: x.pct_result, reverse=True)
    return list_
