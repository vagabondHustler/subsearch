from pathlib import Path

from subsearch.io import file_system, toml_file, windows_registry
from subsearch.runtime.logger import log
from subsearch.runtime.model import Subtitle
from subsearch.parsing import imdb_lookup, release_parser
from subsearch.runtime.constants import APP_PATHS, DEVICE_INFO, FILE_PATHS, VIDEO_FILE


class Bootstrap:
    def __init__(self, pref_counter: float) -> None:
        self.start = pref_counter
        log.brackets("Initializing")

        self.api_calls_made: dict[str, int] = {}
        self.ran_download_tab = False
        self.accepted_subtitles: list[Subtitle] = []
        self.rejected_subtitles: list[Subtitle] = []
        self.manually_accepted_subtitles: list[Subtitle] = []
        self.release_data = release_parser.no_release_data()
        self.provider_urls = release_parser.CreateProviderUrls.no_urls()
        self.file_exist = VIDEO_FILE.file_exist
        self.autoload_src: Path = Path("")

        self.downloaded_subtitles: int = 0
        self.downloaded_subtitle_archives: int = 0
        self.extracted_subtitle_archives: int = 0
        self.user_downloaded_files = False

        log.stdout("Verifing files and paths", level="debug")
        self.setup_file_system()
        self.language_data = toml_file.load_toml_data(FILE_PATHS.subtitle_languages)
        self.app_config = toml_file.get_config_session().snapshot()
        if not windows_registry.check_long_paths_enabled():
            self._notify_user()

        log.dataclass(DEVICE_INFO, level="debug", print_allowed=False)
        log.dataclass(self.app_config, level="debug", print_allowed=False)

        log.stdout("Initializing system tray icon", level="debug")
        from subsearch.ui.system_tray import SystemTray

        self.system_tray = SystemTray(enabled=self.app_config.system_tray)
        self.system_tray.start()

        if self.file_exist:
            VIDEO_FILE.file_hash = file_system.get_file_hash(VIDEO_FILE.file_path)
            log.dataclass(VIDEO_FILE, level="debug", print_allowed=False)
            file_system.create_directory(VIDEO_FILE.file_directory)
            self.release_data = release_parser.get_release_data(VIDEO_FILE.filename)
            self.update_imdb_id()
            log.dataclass(self.release_data, level="debug", print_allowed=False)
            provider_urls = release_parser.CreateProviderUrls(self.app_config, self.release_data, self.language_data)
            self.provider_urls = provider_urls.retrieve_urls()
            log.dataclass(self.provider_urls, level="debug", print_allowed=False)
            self.search_kwargs = dict(
                release_data=self.release_data,
                app_config=self.app_config,
                provider_urls=self.provider_urls,
                language_data=self.language_data,
            )
        log.task_completed()

    def update_imdb_id(self) -> None:
        find_id = imdb_lookup.ImdbIdLookup(
            self.release_data.title,
            self.release_data.year,
            self.release_data.tvseries,
        )
        self.release_data.imdb_id = find_id.imdb_id

    def setup_file_system(self) -> None:
        file_system.create_directory(APP_PATHS.tmp_dir)
        file_system.create_directory(APP_PATHS.appdata_subsearch)
        toml_file.resolve_on_integrity_failure()
        file_system.del_directory_content(APP_PATHS.tmp_dir)
        if self.file_exist:
            file_system.create_directory(VIDEO_FILE.subs_dir)
            file_system.create_directory(VIDEO_FILE.tmp_dir)

    def all_providers_disabled(self) -> bool:
        if (
            self.app_config.providers["opensubtitles"] is False
            and self.app_config.providers["yifysubtitles_site"] is False
            and self.app_config.providers["subsource_site"] is False
        ):
            return True
        return False

    def resync_app_config(self) -> None:
        self.app_config = toml_file.get_config_session().snapshot()

    def prevent_conflicting_config_settings(self) -> None:
        # TODO
        # make settings exclusive in GUI
        session = toml_file.get_config_session()
        if self.app_config.open_manager_on_no_matches and self.app_config.always_open_manager:
            session.write("download.open_manager_on_no_matches", False)
        if (
            self.app_config.post_processing["move_best"]
            and self.app_config.post_processing["move_all"]
        ):
            session.write("post_processing.move_best", False)
        session.commit()
        self.resync_app_config()

    def _notify_user(self) -> None:
        log.stdout("Win32 long paths disabled; paths >260 chars may fail. Set LongPathsEnabled=1 and reboot.")
        log.stdout("https://github.com/vagabondHustler/Win32LongPaths")
