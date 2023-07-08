from pathlib import Path

import cloudscraper
from selectolax.parser import HTMLParser

from subsearch.data.data_objects import (
    AppConfig,
    DownloadData,
    LanguageData,
    PrettifiedDownloadData,
    ProviderUrls,
    ReleaseData,
    SubsceneCookie,
)
from subsearch.utils import io_json


class CustomSubsceneHeader:
    def __init__(self, app_config: AppConfig) -> None:
        self.app_config = app_config

    def _get_hearing_impaired_int(self) -> int:
        if self.app_config.hearing_impaired and self.app_config.non_hearing_impaired:
            value = 0
        if self.app_config.hearing_impaired and not self.app_config.non_hearing_impaired:
            value = 1
        if self.app_config.non_hearing_impaired and not self.app_config.hearing_impaired:
            value = 2
        return value

    def _get_cookie(self) -> SubsceneCookie:
        subscene_cookie = SubsceneCookie(
            dark_theme=False,
            sort_subtitle_by_date="false",
            language_filter=io_json.get_language_data().subscene_id,
            hearing_impaired=self._get_hearing_impaired_int(),
            foreigen_only=self.app_config.foreign_only,
        )
        return subscene_cookie

    def set_cookie_values(self) -> str:
        data = self._get_cookie()
        dark_theme = f"DarkTheme={data.dark_theme}"
        sort_subtitle_by_date = f"SortSubtitlesByDate={data.sort_subtitle_by_date}"
        language_filter = f"LanguageFilter={data.language_filter}"
        hearing_impaired = f"HearingImpaired={data.hearing_impaired}"
        foreign_only = f"ForeignOnly={data.foreigen_only}"
        return f"{dark_theme}; {sort_subtitle_by_date}; {language_filter}; {hearing_impaired}; {foreign_only}"

    def create_header(self) -> dict[str, str]:
        cookie_values = self.set_cookie_values()
        return {"Cookie": cookie_values}


class ProviderParameters:
    """
    Parameters for provider
    """

    def __init__(self, **kwargs):
        release_data: ReleaseData = kwargs["release_data"]
        app_config: AppConfig = kwargs["app_config"]
        provider_urls: ProviderUrls = kwargs["provider_urls"]
        language_data: LanguageData = kwargs["language_data"]

        self.app_config = app_config

        # file parameters
        self.title = release_data.title
        self.year = release_data.year
        self.season = release_data.season
        self.season_ordinal = release_data.season_ordinal
        self.episode = release_data.episode
        self.episode_ordinal = release_data.episode_ordinal
        self.tvseries = release_data.tvseries
        self.release = release_data.release
        self.group = release_data.group
        self.file_hash = release_data.file_hash
        # user parameters
        self.current_language = app_config.current_language
        self.hi_sub = app_config.hearing_impaired
        self.non_hi_sub = app_config.non_hearing_impaired
        self.percentage_threashold = app_config.percentage_threshold
        self.manual_download_fail = app_config.manual_download_fail
        self.manual_download_mode = app_config.manual_download_mode
        # provider url data
        self.url_subscene = provider_urls.subscene
        self.url_opensubtitles = provider_urls.opensubtitles
        self.url_opensubtitles_hash = provider_urls.opensubtitles_hash
        self.url_yifysubtitles = provider_urls.yifysubtitles

        self.language_data = language_data

    def is_threshold_met(self, key: str, pct_result: int) -> bool:
        """Checks if the percentage threshold is met or if the given 'key' contains a title for a TV series.

        Args:
            key (str): Containing the data to be checked for matching with tvseries name
            pct_result (int): Percentage value to compare with "percentage_threshold"

        Returns:
            bool : True or False depending on whether the percentage threshold is met or not
                   and tvseries title is matching or not.
        """
        if pct_result >= self.percentage_threashold or (
            self.title and f"{self.season}{self.episode}" in key.lower() and self.tvseries
        ):
            return True
        return False


def get_cloudscraper():
    return cloudscraper.create_scraper(browser={"browser": "chrome", "platform": "android", "desktop": False})


def get_html_parser(url: str, header_=None):
    """
    Returns a parsed HTML from a given URL using cloudscraper package.

    Args:
        url (str): The URL from where HTML is to be fetched, parsed and returned.

    Returns:
        A `HTMLParser` object which has the parsed HTML content of the given URL text as its attributes.

    """

    scraper = get_cloudscraper()
    if header_ is None:
        response = scraper.get(url)
    else:
        response = scraper.get(url, headers=header_)
    return HTMLParser(response.text)


def create_download_data(provider: str, tmp_directory: Path, to_be_downloaded: dict[str, str]) -> list[DownloadData]:
    """
    Creates a list of data for each downloaded file.

    Args:
        provider (str): The name of the file provider.
        tmp_directory (str): The directory where the temporary downloaded files will be saved.
        to_be_downloaded (dict[str,str]): A dictionary with the name and url of each file to be downloaded.

    Returns:
        List[DownloadData]: A list containing metadata for each downloaded file.
    """
    download_info = []
    idx_lenght = len(to_be_downloaded)
    for idx_num, (name, url) in enumerate(to_be_downloaded.items(), start=1):
        file_path = f"{tmp_directory}\\{provider}_{idx_num}.zip"
        data = DownloadData(provider, name, file_path, url, idx_num, idx_lenght)
        download_info.append(data)
    return download_info


def prettify_download_data(provider: str, key: str, value: str, percentage_result: int) -> PrettifiedDownloadData:
    """
    Prettify the provided download data and return as UpdatedDownloadData object.

    Args:
        provider (str): The metadata provider.
        key (str): Key of the meta-data.
        value (str): Value of the key respective to input key.
        percentage_result (int): Percentage value indicating the match between the found metadata
                                and input query.

    Returns:
        PrettifiedDownloadData: An instance of PrettifiedDownloadData class populated with download data.

    """
    lenght_str = sum(1 for _char in f"{percentage_result:>3}% match:")
    number_of_spaces = " " * lenght_str
    pct_result_string = f"{percentage_result:>3}% match: {key}"
    url = f"{number_of_spaces} {value}"
    data = PrettifiedDownloadData(provider, key, value, percentage_result, pct_result_string, url)
    return data


def sort_prettified_data(list_: list[PrettifiedDownloadData]) -> list[PrettifiedDownloadData]:
    """
    Sorts the list of PrettifiedDownloadData objects based on percentage result from Highest to Lowest.

    Args:
        list_ (list): a list of PrettifiedDownloadData objects

    Returns:
        list: A sorted list of PrettifiedDownloadData objects in descending order by Percentage result.
    """
    list_.sort(key=lambda x: x.pct_result, reverse=True)
    return list_
