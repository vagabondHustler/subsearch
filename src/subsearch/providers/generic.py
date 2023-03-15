import cloudscraper
from selectolax.parser import HTMLParser

from subsearch.data.data_objects import (
    AppConfig,
    DownloadMetaData,
    FormattedMetadata,
    LanguageData,
    ProviderUrls,
    ReleaseData,
)


class ProviderParameters:
    """
    Parameters for provider
    """

    def __init__(self, **kwargs):
        release_data: ReleaseData = kwargs["release_data"]
        app_config: AppConfig = kwargs["app_config"]
        provider_urls: ProviderUrls = kwargs["provider_urls"]
        language_data: LanguageData = kwargs["language_data"]

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


def get_html_parser(url: str):
    """
    Returns a parsed HTML from a given URL using cloudscraper package.

    Args:
        url (str): The URL from where HTML is to be fetched, parsed and returned.

    Returns:
        A `HTMLParser` object which has the parsed HTML content of the given URL text as its attributes.

    """

    scraper = get_cloudscraper()
    response = scraper.get(url)
    return HTMLParser(response.text)


def pack_download_data(provider_: str, video_tmp_directory: str, to_be_downloaded: dict[str, str]) -> list[DownloadMetaData]:
    """
    Creates a list of metadata for each downloaded file.

    Args:
        provider_ (str): The name of the file provider.
        video_tmp_directory (str): The directory where the temporary downloaded files will be saved.
        to_be_downloaded (dict[str,str]): A dictionary with the name and url of each file to be downloaded.

    Returns:
        List[DownloadMetaData]: A list containing metadata for each downloaded file.
    """
    download_info = []
    tbd_lenght = len(to_be_downloaded)
    for zip_idx, (zip_name, zip_url) in enumerate(to_be_downloaded.items(), start=1):
        zip_fp = f"{video_tmp_directory}\\{provider_}_{zip_idx}.zip"
        data = DownloadMetaData(
            provider=provider_, name=zip_name, file_path=zip_fp, url=zip_url, idx_num=zip_idx, idx_lenght=tbd_lenght
        )
        download_info.append(data)
    return download_info


def format_key_value_pct(provider_: str, key: str, value: str, percentage_result_: int) -> FormattedMetadata:
    """
    Formats the provided key, value pair with percentage match result and returns as
    FormattedMetadata object.

    Args:
        provider_ (str): The metadata provider.
        key (str): Key of the meta-data.
        value (str): Value of the key respective to input key.
        percentage_result_ (int): Percentage value indicating the match between the found metadata
                                and input query.

    Returns:
        FormattedMetadata: An instance of FormattedMetadata class populated with formatted metadata.

    """
    lenght_str = sum(1 for char in f"{percentage_result_:>3}% match:")
    number_of_spaces = " " * lenght_str
    _match_release = f"{percentage_result_:>3}% match: {key}"
    _url = f"{number_of_spaces} {value}"
    data = FormattedMetadata(
        provider=provider_,
        release=key,
        url=value,
        pct_result=percentage_result_,
        formatted_release=_match_release,
        formatted_url=_url,
    )
    return data


def sort_download_metadata(list_: list[FormattedMetadata]) -> list[FormattedMetadata]:
    """
    Sorts the list of FormattedMetadata objects based on percentage result from Highest to Lowest.

    Args:
        list_ (list): a list of FormattedMetadata objects

    Returns:
        list: A sorted list of FormattedMetadata objects in descending order by Percentage result.
    """
    list_.sort(key=lambda x: x.pct_result, reverse=True)
    return list_
