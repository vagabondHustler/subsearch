from typing import Any

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


class ProviderDataContainer:
    def __init__(self, **kwargs) -> None:
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
        self.current_language = app_config.language
        self.hi_sub = app_config.hearing_impaired
        self.non_hi_sub = app_config.non_hearing_impaired
        self.percentage_threashold = app_config.accept_threshold
        self.manual_download_on_fail = app_config.open_on_no_matches
        # provider url data
        self.url_opensubtitles = provider_urls.opensubtitles
        self.url_opensubtitles_hash = provider_urls.opensubtitles_hash
        self.url_yifysubtitles = provider_urls.yifysubtitles
        self.url_subsource = provider_urls.subsource

        self.filehash = VIDEO_FILE.file_hash
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


class ProviderHelper(ProviderDataContainer):
    def __init__(self, **kwargs) -> None:
        ProviderDataContainer.__init__(self, **kwargs)
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

    def subtitle_hi_match(self, data: dict[str, Any]) -> bool:
        if self.hi_sub and self.non_hi_sub:
            pass
        else:
            if not self.hi_sub and data["hi"] == 1:
                return False
            if not self.non_hi_sub and data["hi"] == 0:
                return False
        return True

    def subtitle_language_match(self, data: dict[str, Any]) -> bool:
        if self.current_language.lower() != data["lang"].lower():
            return False
        return True

    def keys_exsist(self, data: dict[str, Any], keys: list[str]) -> bool:
        for key in keys:
            if key not in data:
                return False
        return True


def is_threshold_met(cls: "ProviderDataContainer", pct_result: int) -> bool:
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
