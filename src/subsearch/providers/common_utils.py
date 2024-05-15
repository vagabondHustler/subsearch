import cloudscraper
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


class BaseProviderDataContainer:
    def __init__(self, **kwargs) -> None:
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
        self.current_language = app_config.language
        self.hi_sub = app_config.hearing_impaired
        self.non_hi_sub = app_config.non_hearing_impaired
        self.percentage_threashold = app_config.accept_threshold
        self.manual_download_on_fail = app_config.open_on_no_matches
        # provider url data
        self.url_opensubtitles = provider_urls.opensubtitles
        self.url_opensubtitles_hash = provider_urls.opensubtitles_hash
        self.url_yifysubtitles = provider_urls.yifysubtitles

        self.language_data = language_data
        self.filehash = VIDEO_FILE.file_hash


class ProviderHelper(BaseProviderDataContainer):
    def __init__(self, **kwargs) -> None:
        BaseProviderDataContainer.__init__(self, **kwargs)
        self._accepted_subtitles: list[Subtitle] = []
        self._rejected_subtitles: list[Subtitle] = []

    def _process_subtitle_data(self, provider_name: str, subtitle_data: dict[str, str]):
        if not subtitle_data:
            return None

        for subtitle_name, subtitle_url in subtitle_data.items():
            pct_result = string_parser.calculate_match(subtitle_name, self.release)
            log.subtitle_match(
                provider=provider_name,
                subtitle_name=subtitle_name,
                result=pct_result,
                threshold=self.app_config.accept_threshold,
            )
            if is_threshold_met(self, pct_result):
                subtitle = Subtitle(pct_result, provider_name, subtitle_name.lower(), subtitle_url)
                self._accepted_subtitles.append(subtitle)
            else:
                subtitle = Subtitle(pct_result, provider_name, subtitle_name.lower(), subtitle_url)
                self._rejected_subtitles.append(subtitle)


def is_threshold_met(cls: "BaseProviderDataContainer", pct_result: int) -> bool:
    if pct_result >= cls.percentage_threashold:
        return True
    return False


def get_cloudscraper() -> cloudscraper.CloudScraper:
    return cloudscraper.create_scraper(browser={"browser": "chrome", "platform": "android", "desktop": False})


def get_html_parser(url: str, header_=None) -> HTMLParser:
    scraper = get_cloudscraper()
    if header_ is None:
        response = scraper.get(url)
    else:
        response = scraper.get(url, headers=header_)
    return HTMLParser(response.text)
