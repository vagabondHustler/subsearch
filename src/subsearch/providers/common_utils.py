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
    SubtitleUndetermined,
)
from subsearch.utils import string_parser


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
    undetermined_subtitles: list[SubtitleUndetermined] = []

    def __init__(self, master: "ProviderHelper", *args, **kwargs) -> None:
        self._provider_name = master.provider_name
        self._subtitle_name = master.subtitle_name
        self._precentage_result = 0
        self._subtitle_download_url = master.subtitle_download_url
        self._release_name = VIDEO_FILE.filename
        self._accept_threshold = master.accept_threshold
        self._subtitle_met_threashold = master.subtitle_met_threashold
        self._force_undetermined = master.force_undetermined
        self._post_request_data = master.post_request_data
        self.master = master

    @property
    def _subtitle(self) -> Subtitle:
        subtitle = Subtitle(
            self._precentage_result,
            self._provider_name,
            self._subtitle_name.lower(),
            self._subtitle_download_url,
        )
        return subtitle

    @property
    def _subtitle_undetermined(self, *args, **kwargs) -> SubtitleUndetermined:
        subtitle = SubtitleUndetermined(
            provider_name=self._provider_name,
            precentage_result=self._precentage_result,
            passed_threshold=self._subtitle_met_threashold,
            data=self._post_request_data,
        )
        return subtitle

    def prepare_subtitle(self) -> None:
        self.set_percentage_result()
        self.log_subtitle_match()
        self.populate_correct_subtitle_list()

    def set_percentage_result(self) -> None:
        self._precentage_result = string_parser.calculate_match(self._subtitle_name, self._release_name)

    def log_subtitle_match(self) -> None:
        log.subtitle_match(
            self._provider_name,
            self._subtitle_name,
            self._precentage_result,
            self._accept_threshold,
        )

    def populate_correct_subtitle_list(self) -> None:
        if self.master.threshold_met(self._precentage_result):
            if self._force_undetermined:
                _PrepareSubtitleDownload.undetermined_subtitles.append(self._subtitle_undetermined)
            else:
                _PrepareSubtitleDownload.accepted_subtitles.append(self._subtitle)
            return None
        _PrepareSubtitleDownload.rejected_subtitles.append(self._subtitle)


class ProviderHelper(ProviderDataContainer):

    def __init__(self, *args, **kwargs) -> None:
        ProviderDataContainer.__init__(self, *args, **kwargs)
        self.provider_name = ""
        self.subtitle_name = ""
        self.subtitle_download_url = ""
        self.subtitle_met_threashold = False

    def _set_subtitle_cls_vars(self, *args, **kwargs) -> None:
        self.provider_name: str = args[0]
        self.subtitle_name: str = args[1]
        self.subtitle_download_url: str = args[2]
        self.force_undetermined: bool = kwargs.get("force_undetermined", False)
        self.post_request_data: dict[str, Any] = kwargs.get("post_request_data", {})

    @property
    def accepted_subtitles(self) -> list[Subtitle]:
        return _PrepareSubtitleDownload.accepted_subtitles

    @property
    def rejected_subtitles(self) -> list[Subtitle]:
        return _PrepareSubtitleDownload.rejected_subtitles

    @property
    def undetermined_subtitles(self) -> list[Subtitle]:
        return _PrepareSubtitleDownload.undetermined_subtitles

    def prepare_multiple_subtitles(self, provider_name: str, subtitle_data: dict[str, str], *args, **kwargs) -> None:
        if not subtitle_data:
            return subtitle_data

        for subtitle_name, subtitle_download_url in subtitle_data.items():
            self.prepare_subtitle(provider_name, subtitle_name, subtitle_download_url)

    def prepare_subtitle(self, provider_name: str, subtitle_name: str, download_url: str, *args, **kwargs) -> None:
        self._set_subtitle_cls_vars(provider_name, subtitle_name, download_url, *args, **kwargs)
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
            i = True
        else:
            i = False
        self.subtitle_met_threashold = i
        return i


def get_cloudscraper() -> cloudscraper.CloudScraper:
    return cloudscraper.create_scraper(browser={"browser": "chrome", "platform": "android", "desktop": False})


def get_html_parser(url: str, header_=None) -> HTMLParser:
    scraper = get_cloudscraper()
    if header_ is None:
        response = scraper.get(url)
    else:
        response = scraper.get(url, headers=header_)
    return HTMLParser(response.text)
