import sys
from pathlib import Path

from subsearch.io import file_system, file_tracker, language_data, windows_registry
from subsearch.parsing import imdb_lookup, release_parser
from subsearch.providers.provider_helper import SubtitleResults
from subsearch.runtime.config import config_session
from subsearch.runtime.config.constants import APP_PATHS, DEVICE_INFO, VIDEO_FILE
from subsearch.runtime.logging.logger import log
from subsearch.runtime.models.model import (
    AppMode,
    ProviderDiagnosticStatus,
    ProviderResult,
    Subtitle,
)


class Bootstrap:
    def __init__(self, pref_counter: float) -> None:
        self.start = pref_counter
        self.api_calls_made: dict[str, int] = {}
        self.ran_download_tab = False
        self.subtitle_results = SubtitleResults()
        self.manually_accepted_subtitles: list[Subtitle] = []
        self.health_reports: list[ProviderResult] = []
        self.release_data = release_parser.no_release_data()
        self.provider_urls = release_parser.CreateProviderUrls.no_urls()
        self.autoload_src: Path = Path("")

        self.downloaded_subtitle_archives: int = 0
        self.extracted_subtitle_archives: int = 0
        self.user_downloaded_files = False

        log.debug(f"sys.argv: {sys.argv}")
        log.debug(
            f"Video file {'found' if VIDEO_FILE.file_exists else 'not found'}: {VIDEO_FILE.file_path or 'none'}",
        )
        log.info("Verifying files and paths")
        self.setup_file_system()
        self.language_data = language_data.load_language_data()
        self.app_config = config_session.get_config_session().snapshot()
        windows_registry.reconcile_shell_integration()
        self.app_mode = self._resolve_app_mode()
        if not windows_registry.check_long_paths_enabled():
            self._notify_user()

        log.dataclass(DEVICE_INFO, level="debug", to_console=False)
        log.dataclass(self.app_config, level="debug", to_console=False)

        log.debug("Initializing system tray icon")
        from subsearch.ui.system_tray import SystemTray

        self.system_tray = SystemTray(enabled=self.app_config.system_tray)
        self.system_tray.start()

        if self.gui_may_open:
            log.debug("GUI warmup triggered")
            from subsearch.ui import warmup

            warmup.start_warmup()

        if self.app_mode is not AppMode.SETTINGS:
            self.rebuild_search_inputs()
        log.event("task_completed")

    def ensure_search_mode(self) -> None:
        if self.app_mode is AppMode.SETTINGS:
            self.app_mode = AppMode.SEARCH_MANUAL

    def rebuild_search_inputs(self, imdb_id: str = "") -> None:
        self._anchor_working_directory()
        VIDEO_FILE.file_hash = file_system.get_file_hash(VIDEO_FILE.file_path) if VIDEO_FILE.file_exists else ""
        log.dataclass(VIDEO_FILE, level="debug", to_console=False)
        if VIDEO_FILE.file_directory != Path(""):
            file_system.create_directory(VIDEO_FILE.file_directory)
            self._create_search_directories()
        self.subtitle_results = SubtitleResults()
        self.health_reports = []
        self.release_data = release_parser.get_release_info(VIDEO_FILE.filename)
        self.update_imdb_id(imdb_id)
        log.dataclass(self.release_data, level="debug", to_console=False)
        provider_urls = release_parser.CreateProviderUrls(
            self.app_config, self.release_data, self.language_data, VIDEO_FILE.file_hash
        )
        self.provider_urls = provider_urls.retrieve_urls()
        log.dataclass(self.provider_urls, level="debug", to_console=False)
        self.search_kwargs = dict(
            release_data=self.release_data,
            app_config=self.app_config,
            provider_urls=self.provider_urls,
            language_data=self.language_data,
            filename=VIDEO_FILE.filename,
            subtitle_results=self.subtitle_results,
        )

    def update_imdb_id(self, imdb_id: str = "") -> None:
        if imdb_id:
            self.release_data.imdb_id = imdb_id
            self.health_reports.append(ProviderResult("imdb", ProviderDiagnosticStatus.OK, 1))
            return
        find_id = imdb_lookup.ImdbIdLookup(
            self.release_data.title,
            self.release_data.year,
            self.release_data.tvseries,
        )
        self.release_data.imdb_id = find_id.imdb_id
        found_subtitles = 1 if find_id.imdb_id else 0
        self.health_reports.append(ProviderResult("imdb", find_id.diagnostic_status, found_subtitles))

    def setup_file_system(self) -> None:
        file_system.create_directory(APP_PATHS.tmp_dir)
        file_system.create_directory(APP_PATHS.appdata_subsearch)
        file_tracker.get_file_tracker().reclaim_after_crash()
        file_system.del_directory_content(APP_PATHS.tmp_dir)
        if VIDEO_FILE.file_exists:
            self._create_search_directories()

    def _create_search_directories(self) -> None:
        tracker = file_tracker.get_file_tracker()
        for directory in (VIDEO_FILE.subs_dir, VIDEO_FILE.tmp_dir):
            if file_system.create_directory(directory):
                tracker.track(directory)

    def _anchor_working_directory(self) -> None:
        if VIDEO_FILE.file_exists or VIDEO_FILE.file_directory != Path(""):
            return
        configured = self.app_config.download_manager_working_directory.strip()
        working_directory = Path(configured) if configured else Path.home() / "Downloads"
        # An explicitly chosen folder is used as the subtitle destination directly;
        # only the default Downloads location gets a "subs" subfolder so subtitles
        # are not dropped loose into the user's Downloads.
        VIDEO_FILE.file_directory = working_directory
        VIDEO_FILE.file_path = working_directory / (VIDEO_FILE.filename + VIDEO_FILE.file_extension)
        VIDEO_FILE.subs_dir = working_directory if configured else working_directory / "subs"
        VIDEO_FILE.tmp_dir = working_directory / "tmp_subsearch"

    @property
    def accepted_subtitles(self) -> list[Subtitle]:
        return self.subtitle_results.accepted

    @property
    def rejected_subtitles(self) -> list[Subtitle]:
        return self.subtitle_results.rejected

    def _resolve_app_mode(self) -> AppMode:
        if "--preview" in sys.argv:
            return AppMode.DEV
        if not self._has_path_argument():
            return AppMode.SETTINGS
        if not VIDEO_FILE.file_exists:
            return AppMode.SEARCH_MANUAL
        if self.app_config.search_mode == "manual":
            return AppMode.SEARCH_MANUAL
        if self.app_config.search_mode == "automatic":
            return AppMode.SEARCH_AUTOMATIC
        return AppMode.SEARCH_HYBRID

    @staticmethod
    def _has_path_argument() -> bool:
        return any("\\" in arg for arg in sys.argv[1:])

    @property
    def gui_may_open(self) -> bool:
        return self.app_mode in (AppMode.SETTINGS, AppMode.SEARCH_MANUAL, AppMode.SEARCH_HYBRID, AppMode.DEV)

    def all_providers_disabled(self) -> bool:
        if (
            self.app_config.providers["opensubtitles"] is False
            and self.app_config.providers["yifysubtitles_site"] is False
            and self.app_config.providers["subsource_site"] is False
        ):
            return True
        return False

    def resync_app_config(self) -> None:
        self.app_config = config_session.get_config_session().snapshot()

    def prevent_conflicting_config_settings(self) -> None:
        session = config_session.get_config_session()
        if self.app_config.post_processing["move_best"] and self.app_config.post_processing["move_all"]:
            session.write("post_processing.move_best", False)
        session.commit()
        self.resync_app_config()

    def _notify_user(self) -> None:
        log.info("Win32 long paths disabled; paths >260 chars may fail. Set LongPathsEnabled=1 and reboot.")
        log.info("https://github.com/vagabondHustler/Win32LongPaths")
