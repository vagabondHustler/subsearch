import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any

from subsearch.io import windows_registry

if TYPE_CHECKING:
    from subsearch.providers.provider_helper import SubtitleResults
    from subsearch.ui.core.system_tray import SystemTray

from subsearch.runtime.config import (
    APP_PATHS,
    DEVICE_INFO,
    PATH_RESOLVER,
    SEARCH_SUBJECT,
    SUPPORTED_PROVIDERS,
    WORKSPACE,
)
from subsearch.runtime.config import session as config_session
from subsearch.runtime.config import (
    shell_integration,
)
from subsearch.runtime.models import (
    AppMode,
    ProviderDiagnosticStatus,
    ProviderResult,
    ProviderUrls,
    ReleaseInfo,
    Subtitle,
)
from subsearch.runtime.recorder import LogLevel, capture


class HeadlessNotificationSink:
    def display_toast(self, title: str, message: str) -> None:
        return None

    def start(self) -> None:
        return None

    def stop(self) -> None:
        return None


class Bootstrap:
    def __init__(self, pref_counter: float) -> None:
        self.start = pref_counter
        self._init_state()
        self._log_boot_environment()
        self._prepare_runtime()
        self._start_system_tray()
        self._lazy_load_ui()
        if self.app_mode is not AppMode.SETTINGS:
            self.rebuild_search_inputs()
        capture("Boot completed")

    def _init_state(self) -> None:
        self.api_calls_made: dict[str, int] = {}
        self.subtitle_results: "SubtitleResults | None" = None
        self.system_tray: "SystemTray | HeadlessNotificationSink"
        self.manual_accepted_subtitles: list[Subtitle] = []
        self.health_reports: list[ProviderResult] = []
        self.pending_notifications: list[tuple[str, str]] = []
        self.language_data: dict[str, Any] = {}
        self.release_data = ReleaseInfo("", 0, "", "", "", "", False, "", "", "")
        self.provider_urls = ProviderUrls([], [], [], [], [])
        self.autoload_src: Path = Path("")
        self.downloaded_subtitle_archives: int = 0
        self.extracted_subtitle_archives: int = 0
        self._search_runtime_ready = False

    def _log_boot_environment(self) -> None:
        capture(f"sys.argv: {sys.argv}", level=LogLevel.DEBUG)
        presence = "found" if SEARCH_SUBJECT.file_exists else "not found"
        capture(f"Video file {presence}: {SEARCH_SUBJECT.file_path or 'none'}", level=LogLevel.DEBUG)

    def _prepare_runtime(self) -> None:
        capture("Verifying files and paths")
        self.app_config = config_session.get_config_session().snapshot()
        shell_integration.reconcile_shell_integration()
        self.app_mode = self._resolve_app_mode()
        if not windows_registry.check_long_paths_enabled():
            self._notify_user()
        capture(repr(DEVICE_INFO), level=LogLevel.DEBUG)
        capture(repr(self.app_config), level=LogLevel.DEBUG)

    def _start_system_tray(self) -> None:
        capture("Initializing system tray icon", level=LogLevel.DEBUG)
        if not self.ui_may_open:
            self.system_tray = HeadlessNotificationSink()
            return
        from subsearch.ui.core.system_tray import SystemTray

        self.system_tray = SystemTray(
            enabled=self.app_config.system_tray,
            display_duration_ms=round(self.app_config.notification_display_duration * 1000),
            play_sound=self.app_config.notification_play_sound,
        )
        self.system_tray.start()

    def ensure_search_mode(self) -> None:
        if self.app_mode is AppMode.SETTINGS:
            self.app_mode = AppMode.SEARCH_MANUAL

    def rebuild_search_inputs(self, imdb_id: str = "", tvseries: bool | None = None) -> None:
        self._prepare_search_runtime()
        from subsearch.io import file_system
        from subsearch.parsing import release_parser
        from subsearch.providers.provider_helper import SubtitleResults

        self._anchor_working_directory()
        file_path = SEARCH_SUBJECT.file_path
        SEARCH_SUBJECT.file_hash = file_system.get_file_hash(file_path) if file_path is not None else ""
        capture(repr(SEARCH_SUBJECT), level=LogLevel.DEBUG)
        capture(repr(WORKSPACE), level=LogLevel.DEBUG)
        if WORKSPACE.file_directory != Path(""):
            file_system.create_directory(WORKSPACE.file_directory)
            self._create_search_directories()
        self.subtitle_results = SubtitleResults()
        self.health_reports = []
        self.release_data = release_parser.get_release_info(SEARCH_SUBJECT.search_term)
        if tvseries is not None:
            self.release_data.tvseries = tvseries
        self.update_imdb_id(imdb_id)
        capture(repr(self.release_data), level=LogLevel.DEBUG)
        provider_urls = release_parser.CreateProviderUrls(
            self.app_config, self.release_data, self.language_data, SEARCH_SUBJECT.file_hash
        )
        self.provider_urls = provider_urls.retrieve_urls()
        capture(repr(self.provider_urls), level=LogLevel.DEBUG)
        self.search_kwargs = dict(
            release_data=self.release_data,
            app_config=self.app_config,
            provider_urls=self.provider_urls,
            language_data=self.language_data,
            filename=SEARCH_SUBJECT.search_term,
            subtitle_results=self.subtitle_results,
        )

    def _prepare_search_runtime(self) -> None:
        if self._search_runtime_ready:
            return
        from subsearch.io import language_data

        self.setup_file_system()
        self.language_data = language_data.load_language_data()
        self._search_runtime_ready = True

    def _lazy_load_ui(self) -> None:
        if not self.ui_may_open:
            return
        capture("Lazy loading UI", level=LogLevel.DEBUG)
        from subsearch.ui import warmup

        warmup.start_warmup()
        capture("Lazy loading UI done", level=LogLevel.DEBUG)

    def update_imdb_id(self, imdb_id: str = "") -> None:
        if imdb_id:
            self.release_data.imdb_id = imdb_id
            self.health_reports.append(ProviderResult("imdb", ProviderDiagnosticStatus.OK, 1))
            return
        from subsearch.parsing import imdb_lookup

        find_id = imdb_lookup.ImdbIdLookup(
            self.release_data.title,
            self.release_data.year,
            self.release_data.tvseries,
        )
        self.release_data.imdb_id = find_id.imdb_id
        found_subtitles = 1 if find_id.imdb_id else 0
        self.health_reports.append(ProviderResult("imdb", find_id.diagnostic_status, found_subtitles))

    def setup_file_system(self) -> None:
        from subsearch.io import file_system
        from subsearch.runtime.recorder import get_file_tracker

        file_system.create_directory(APP_PATHS.tmp_dir)
        file_system.create_directory(APP_PATHS.appdata_subsearch)
        get_file_tracker().reclaim_after_crash()
        file_system.del_directory_content(APP_PATHS.tmp_dir)
        if SEARCH_SUBJECT.file_exists:
            self._create_search_directories()

    def _create_search_directories(self) -> None:
        from subsearch.io import file_system
        from subsearch.runtime.recorder import get_file_tracker

        tracker = get_file_tracker()
        for directory in (WORKSPACE.extraction_directory, WORKSPACE.download_directory):
            if file_system.create_directory(directory):
                tracker.track(directory)

    def _anchor_working_directory(self) -> None:
        if SEARCH_SUBJECT.file_exists:
            return
        resolved = PATH_RESOLVER.resolve_directories(self.app_config)
        WORKSPACE.file_directory = Path.home() / "Downloads"
        WORKSPACE.extraction_directory = resolved.extraction_directory
        WORKSPACE.download_directory = resolved.download_directory

    @property
    def accepted_subtitles(self) -> list[Subtitle]:
        if self.subtitle_results is None:
            return []
        return self.subtitle_results.accepted

    @property
    def rejected_subtitles(self) -> list[Subtitle]:
        if self.subtitle_results is None:
            return []
        return self.subtitle_results.rejected

    def _resolve_app_mode(self) -> AppMode:
        if not self._has_path_argument():
            return AppMode.SETTINGS
        if not SEARCH_SUBJECT.file_exists:
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
    def ui_may_open(self) -> bool:
        return self.app_mode in (AppMode.SETTINGS, AppMode.SEARCH_MANUAL, AppMode.SEARCH_HYBRID)

    def all_providers_disabled(self) -> bool:
        return not any(self.app_config.providers.get(provider, False) for provider in SUPPORTED_PROVIDERS)

    def resync_app_config(self) -> None:
        self.app_config = config_session.get_config_session().snapshot()

    def _notify_user(self) -> None:
        capture("Win32 long paths disabled; paths >260 chars may fail. Set LongPathsEnabled=1 and reboot.")
        capture("https://github.com/vagabondHustler/Win32LongPaths")
