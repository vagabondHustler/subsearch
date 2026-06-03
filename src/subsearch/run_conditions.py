from typing import Callable

from subsearch.bootstrap import Bootstrap


class RunConditions:
    def __init__(self, bootstrap: Bootstrap) -> None:
        self.bootstrap = bootstrap
        self.sync_state()

    def sync_state(self) -> None:
        self.app_config = self.bootstrap.app_config
        self.file_exist = self.bootstrap.file_exist
        self.release_data = self.bootstrap.release_data
        self.provider_urls = self.bootstrap.provider_urls
        self.language_data = self.bootstrap.language_data
        self.accepted_subtitles = self.bootstrap.accepted_subtitles
        self.rejected_subtitles = self.bootstrap.rejected_subtitles
        self.downloaded_subtitle_archives = self.bootstrap.downloaded_subtitle_archives
        self.extracted_subtitle_archives = self.bootstrap.extracted_subtitle_archives

    def language_supports_provider(self, provider: str) -> bool:
        language = self.app_config.selected_language
        incompatible_providers = self.language_data[language]["incompatibility"]
        return provider not in incompatible_providers

    @property
    def has_accepted(self) -> bool:
        return len(self.accepted_subtitles) >= 1

    @property
    def has_rejected(self) -> bool:
        return len(self.rejected_subtitles) >= 1

    @property
    def should_download_files(self) -> bool:
        if not self.has_accepted:
            return False
        if self.app_config.automatic_downloads:
            return True
        return not self.app_config.always_open_manager and not self.app_config.open_manager_on_no_matches

    @property
    def should_open_download_manager(self) -> bool:
        open_no_matches = not self.has_accepted and self.has_rejected and self.app_config.open_manager_on_no_matches
        always_open = (self.has_accepted or self.has_rejected) and self.app_config.always_open_manager
        return open_no_matches or always_open

    def all_conditions_true(self, conditions: "list[bool | Callable[[], bool]]") -> bool:
        return all(condition() if callable(condition) else condition for condition in conditions)

    def conditions_met(self, func_name: str) -> bool:
        self.sync_state()
        post_processing = self.app_config.post_processing
        conditions: dict[str, list[bool | Callable[[], bool]]] = {
            "init_search": [self.file_exist],
            "opensubtitles": [
                self.file_exist,
                lambda: self.language_supports_provider("opensubtitles"),
                self.app_config.providers["opensubtitles"],
            ],
            "yifysubtitles": [
                self.file_exist,
                not self.app_config.only_foreign_parts,
                lambda: self.language_supports_provider("yifysubtitles"),
                not self.release_data.tvseries,
                self.provider_urls.yifysubtitles != "",
                self.app_config.providers["yifysubtitles_site"],
            ],
            "subsource": [
                self.file_exist,
                not self.app_config.only_foreign_parts,
                lambda: self.language_supports_provider("subsource"),
                self.app_config.providers["subsource_site"],
            ],
            "download_files": [self.should_download_files],
            "download_manager": [self.should_open_download_manager],
            "subtitle_post_processing": [self.file_exist],
            "extract_files": [self.downloaded_subtitle_archives >= 1],
            "subtitle_rename": [
                self.extracted_subtitle_archives >= 1,
                post_processing["rename"],
            ],
            "subtitle_move_best": [
                self.extracted_subtitle_archives >= 1,
                post_processing["move_best"],
                not post_processing["move_all"],
            ],
            "subtitle_move_all": [
                self.extracted_subtitle_archives >= 1,
                post_processing["move_all"],
            ],
            "summary_notification": [
                self.file_exist,
                self.app_config.summary_notification,
            ],
            "clean_up": [self.file_exist],
        }

        return self.all_conditions_true(conditions[func_name])
