from pathlib import Path

import cloudscraper
from selectolax.parser import HTMLParser

from subsearch.data.constants import VIDEO_FILE
from subsearch.data.data_classes import (
    AppConfig,
    LanguageData,
    ProviderUrls,
    ReleaseData,
    SkippedSubtitle,
    SubsceneCookie,
    Subtitle,
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


class SearchArguments:
    """
    Helper class for provider
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

        # user parameters
        self.current_language = app_config.current_language
        self.hi_sub = app_config.hearing_impaired
        self.non_hi_sub = app_config.non_hearing_impaired
        self.percentage_threashold = app_config.percentage_threshold
        self.manual_download_on_fail = app_config.manual_download_on_fail
        # provider url data
        self.url_subscene = provider_urls.subscene
        self.url_opensubtitles = provider_urls.opensubtitles
        self.url_opensubtitles_hash = provider_urls.opensubtitles_hash
        self.url_yifysubtitles = provider_urls.yifysubtitles

        self.language_data = language_data
        self.filehash = VIDEO_FILE.file_hash


def is_threshold_met(cls: "SearchArguments", pct_result: int) -> bool:
    if pct_result >= cls.percentage_threashold:
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


def prepare_subtitles_download(provider: str, tmp_dir: Path, to_be_downloaded: dict[str, str]) -> list[Subtitle]:
    download_info = []
    idx_lenght = len(to_be_downloaded)
    for idx_num, (name, url) in enumerate(to_be_downloaded.items(), start=1):
        file_path = f"{tmp_dir}\\{provider}_{idx_num}.zip"
        data = Subtitle(provider, name, file_path, url, idx_num, idx_lenght)
        download_info.append(data)
    return download_info


def prepare_subtitles_skipped(provider: str, key: str, value: str, percentage_result: int) -> SkippedSubtitle:
    lenght_str = sum(1 for _char in f"{percentage_result:>3}% match:")
    number_of_spaces = " " * lenght_str
    pct_result_string = f"{percentage_result:>3}% match: {key}"
    url = f"{number_of_spaces} {value}"
    data = SkippedSubtitle(provider, key, value, percentage_result, pct_result_string, url)
    return data


def sort_skipped_subtitles(list_: list[SkippedSubtitle]) -> list[SkippedSubtitle]:
    """
    Sorts the list of PrettifiedDownloadData objects based on percentage result from Highest to Lowest.

    Args:
        list_ (list): a list of PrettifiedDownloadData objects

    Returns:
        list: A sorted list of PrettifiedDownloadData objects in descending order by Percentage result.
    """
    list_.sort(key=lambda x: x.pct_result, reverse=True)
    return list_
