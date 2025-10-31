import threading
from typing import Any

import cloudscraper
from cloudscraper import CloudScraper
from requests import Response, exceptions
from selectolax.parser import HTMLParser

from subsearch.globals import log
from subsearch.globals.constants import VIDEO_FILE
from subsearch.globals.dataclasses import (
    AppConfig,
    LanguageData,
    ProviderUrls,
    ReleaseData,
    Subtitle,
)
from subsearch.utils import string_parser

api_calls_made: dict[str, int] = {}
_thread_lock = threading.Lock()


class ProviderDataContainer:
    def __init__(self, *args, **kwargs) -> None:
        release_data: ReleaseData = kwargs.get("release_data")
        app_config: AppConfig = kwargs.get("app_config")
        provider_urls: ProviderUrls = kwargs.get("provider_urls")
        language_data: LanguageData = kwargs.get("language_data")

        self.app_config = app_config
        self.release_data = release_data
        self.provider_urls = provider_urls
        self.language_data = language_data

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
        self.imdb_id = release_data.imdb_id

        # user parameters
        self.current_language = app_config.current_language
        self.hearing_impaired = app_config.hearing_impaired
        self.non_hearing_impaired = app_config.non_hearing_impaired
        self.accept_threshold = app_config.accept_threshold
        self.open_on_no_matches = app_config.open_on_no_matches
        self.api_call_limit = app_config.api_call_limit
        self.request_connect_timeout = app_config.request_connect_timeout
        self.request_read_timeout = app_config.request_read_timeout
        self.request_timeout = (self.request_connect_timeout, self.request_read_timeout)
        # provider url data
        self.url_opensubtitles = provider_urls.opensubtitles
        self.url_opensubtitles_hash = provider_urls.opensubtitles_hash
        self.url_yifysubtitles = provider_urls.yifysubtitles
        self.url_subsource = provider_urls.subsource

        self.file_hash = VIDEO_FILE.file_hash
        self.season_no_padding = self._season_no_padding()
        self.episode_no_padding = self._episode_no_padding()
        self.ok_season_episode_pattern = self._ok_season_episode_pattern()

    def _season_no_padding(self) -> str:
        return string_parser.remove_padded_zero(self.release_data.season)

    def _episode_no_padding(self) -> str:
        return string_parser.remove_padded_zero(self.release_data.episode)

    def _ok_season_episode_pattern(self) -> list[str]:
        season_episode_pattern_0 = [
            f"season.{self.season}.",
            f"s{self.season}e{self.episode}.",
            f"s{self.season}.e{self.episode}.",
        ]
        season_episode_pattern_1 = [
            f"season.{self.season_no_padding}.",
            f"s{self.season_no_padding}.e{self.episode_no_padding}.",
        ]
        return season_episode_pattern_0 + season_episode_pattern_1


class _PrepareSubtitleDownload:
    accepted_subtitles: list[Subtitle] = []
    rejected_subtitles: list[Subtitle] = []

    def __init__(self, master: "ProviderHelper", *args, **kwargs) -> None:
        self.provider_name = master.provider_name
        self.subtitle_name = master.subtitle_name
        self.precentage_result = 0
        self.download_url = master.download_url
        self.release_name = VIDEO_FILE.filename
        self.accept_threshold = master.accept_threshold
        self.request_data = master.request_data
        self.master = master

    @property
    def _subtitle(self) -> Subtitle:
        self.subtitle_name = self._sanitize_filename(self.subtitle_name)
        if self.download_url:
            subtitle = self._get_subtitle_no_request_data()
        elif self.request_data:
            subtitle = self._get_subtitle_with_download_url()
        else:
            raise Exception("Subtitle not corectlly populated")
        return subtitle

    def _sanitize_filename(self, filename: str) -> str:
        old_filename = filename
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, "_")
        filename = filename.replace("'", "")
        log.stdout(f"Sanitized {old_filename} to {filename}")
        return filename

    def _get_subtitle_no_request_data(self) -> Subtitle:
        subtitle = Subtitle(
            precentage_result=self.precentage_result,
            provider_name=self.provider_name,
            subtitle_name=self.subtitle_name.lower(),
            download_url=self.download_url,
            request_data={},
        )
        return subtitle

    def _get_subtitle_with_download_url(self) -> Subtitle:
        subtitle = Subtitle(
            precentage_result=self.precentage_result,
            provider_name=self.provider_name,
            subtitle_name=self.subtitle_name.lower(),
            download_url="",
            request_data=self.request_data,
        )
        return subtitle

    def prepare_subtitle(self) -> None:
        self.set_percentage_result()
        self.log_subtitle_match()
        self.populate_correct_subtitle_list()

    def set_percentage_result(self) -> None:
        self.precentage_result = string_parser.calculate_match(self.subtitle_name, self.release_name)

    def log_subtitle_match(self) -> None:
        log.subtitle_match(
            self.provider_name,
            self.subtitle_name,
            self.precentage_result,
            self.accept_threshold,
        )

    def populate_correct_subtitle_list(self) -> None:
        if self.master.threshold_met(self.precentage_result):
            return _PrepareSubtitleDownload.accepted_subtitles.append(self._subtitle)
        return _PrepareSubtitleDownload.rejected_subtitles.append(self._subtitle)


class ProviderHelper(ProviderDataContainer):

    def __init__(self, *args, **kwargs) -> None:
        ProviderDataContainer.__init__(self, *args, **kwargs)
        self.provider_name = ""
        self.subtitle_name = ""
        self.download_url = ""

    def _set_subtitle_cls_vars(self, *args, **kwargs) -> None:
        self.provider_name: str = args[0]
        self.subtitle_name: str = args[1]
        self.download_url: str = args[2]
        self.request_data: dict[str, Any] = kwargs.get("request_data", {}) or args[3]

    @property
    def accepted_subtitles(self) -> list[Subtitle]:
        with _thread_lock:
            return _PrepareSubtitleDownload.accepted_subtitles

    @property
    def rejected_subtitles(self) -> list[Subtitle]:
        with _thread_lock:
            return _PrepareSubtitleDownload.rejected_subtitles

    def prepare_subtitle(self, provider_name: str, subtitle_name: str, download_url: str, request_data: dict) -> None:
        with _thread_lock:
            self._set_subtitle_cls_vars(provider_name, subtitle_name, download_url, request_data)
            prepare = _PrepareSubtitleDownload(self)
            prepare.prepare_subtitle()

    def subtitle_hi_match(self, hi: bool) -> bool:
        if self.hearing_impaired and self.non_hearing_impaired:
            return True
        if not self.hearing_impaired and hi:
            return False
        if not self.non_hearing_impaired and hi:
            return False
        return True

    def subtitle_language_match(self, language: str) -> bool:
        if self.current_language.lower() != language.lower():
            return False
        return True

    def keys_exsist(self, dict_: dict[str, Any], keys: list[str]) -> bool:
        for key in keys:
            if key not in dict_:
                return False
        return True

    def threshold_met(self, precentage_result: int) -> bool:
        if precentage_result >= self.accept_threshold:
            return True
        return False


def get_cloudscraper() -> CloudScraper:
    return cloudscraper.create_scraper(browser={"browser": "chrome", "platform": "android", "desktop": False})


def send_request(url: str, scraper: CloudScraper, timeout: tuple[int, int], header=None) -> Response:
    if header is None:
        return scraper.get(url, timeout=timeout)
    return scraper.get(url, timeout=timeout, headers=header)


def parse_scraper_response(response: Response) -> HTMLParser:
    return HTMLParser(response.text)


def request_parsed_response(url: str, timeout: tuple[int, int], header=None) -> HTMLParser:
    scraper = get_cloudscraper()
    try:
        response = send_request(url, scraper, timeout=timeout, header=header)
    except exceptions.Timeout as e:
        log.stdout(e, level="warning", print_allowed=False)
        return ""
    return parse_scraper_response(response)


def sort_list_by_precentage_result(list_: list) -> list:
    with _thread_lock:
        return sorted(list_, key=lambda i: i.precentage_result, reverse=True)
