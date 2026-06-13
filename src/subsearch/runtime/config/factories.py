import platform
import sys
import tempfile
from pathlib import Path
from typing import Any

from subsearch.runtime.config.static_values import (
    DEFAULT_TOKEN_MULTIPLIERS,
    DEFAULT_TOKEN_WEIGHTS,
    HEALTH_TRACKED_PROVIDERS,
    SUPPORTED_FILE_EXTENSIONS,
    SUPPORTED_PROVIDERS,
)
from subsearch.runtime.config.version import __version__
from subsearch.runtime.models.model import (
    AppPaths,
    FilePaths,
    SystemInfo,
    VideoFile,
    WindowsRegistryPaths,
)

_APP_HOME = Path(__file__).resolve().parent.parent.parent


def get_app_paths() -> AppPaths:
    return AppPaths(
        home=_APP_HOME,
        data=_APP_HOME / "data",
        ui_assets=_APP_HOME / "ui" / "assets",
        providers=_APP_HOME / "providers",
        io=_APP_HOME / "io",
        parsing=_APP_HOME / "parsing",
        tmp_dir=Path(tempfile.gettempdir()) / "tmp_subsearch",
        appdata_subsearch=Path.home() / "AppData" / "Local" / "Subsearch",
    )


def get_file_paths() -> FilePaths:
    return FilePaths(
        log=Path.home() / "AppData" / "Local" / "Subsearch" / "log.log",
        config=Path.home() / "AppData" / "Local" / "Subsearch" / "config.toml",
        subtitle_languages=_APP_HOME / "data" / "subtitle_languages.toml",
    )


def get_default_app_config() -> dict[str, Any]:
    file_extensions = dict.fromkeys(SUPPORTED_FILE_EXTENSIONS, True)
    providers = dict.fromkeys(SUPPORTED_PROVIDERS, True)
    provider_diagnostics = {provider: {"failed_attempts": 0} for provider in HEALTH_TRACKED_PROVIDERS}
    return {
        "language": {
            "selected": "english",
        },
        "search": {
            "accept_threshold": 90,
            "hearing_impaired": True,
            "non_hearing_impaired": True,
            "only_foreign_parts": False,
            "providers": providers,
            "downloads_per_provider": 4,
            "token_weights": {**DEFAULT_TOKEN_WEIGHTS},
            "token_multipliers": {**DEFAULT_TOKEN_MULTIPLIERS},
        },
        "shell_integration": {
            "context_menu": True,
            "context_menu_icon": True,
            "file_extensions": file_extensions,
        },
        "notifications": {
            "system_tray": True,
            "summary_notification": False,
        },
        "download_manager": {
            "search_mode": "hybrid",
            "manually_handle_post_processing": False,
            "use_post_processing_target": True,
            "target_path": ".",
            "working_directory": "",
        },
        "post_processing": {
            "rename": True,
            "move_best": True,
            "move_all": False,
            "target_path": ".",
            "path_resolution": "relative",
            "create_missing_folder": True,
        },
        "application": {
            "show_terminal": False,
            "single_instance": True,
        },
        "network": {
            "request_connect_timeout": 4,
            "request_read_timeout": 5,
        },
        "diagnostics": {
            "enabled": True,
            "failed_attempts_threshold": 3,
            "provider_diagnostics": provider_diagnostics,
        },
        "credentials": {
            "subsource": {
                "api_key_exists": False,
                "api_key": "",
            },
        },
    }


class VideoFileResolver:
    def __init__(self, supported_extensions: list[str]) -> None:
        self._supported_extensions = supported_extensions

    def resolve_from_argv(self) -> VideoFile:
        for argument in sys.argv:
            file_path = self._find_video_file_path(argument)
            if file_path is not None:
                return self._build_from_path(file_path)
        return self._build_empty()

    def re_resolve(self, filename: str, file_directory: Path) -> VideoFile:
        suffix = Path(filename).suffix
        has_video_extension = suffix.lstrip(".") in self._supported_extensions
        file_path = file_directory / filename
        if has_video_extension and file_path.exists():
            return self._build_from_path(file_path)
        return VideoFile(
            file_exists=False,
            filename=Path(filename).stem if has_video_extension else filename,
            file_hash="",
            file_extension=suffix if has_video_extension else "",
            file_path=file_path,
            file_directory=file_directory,
            subs_dir=file_directory / "subs",
            tmp_dir=file_directory / "tmp_subsearch",
        )

    def _find_video_file_path(self, argument: str) -> Path | None:
        argument_path = Path(argument)
        extension = argument_path.suffix.lstrip(".")
        if extension in self._supported_extensions and "\\" in argument:
            return argument_path
        return None

    def _build_from_path(self, file_path: Path) -> VideoFile:
        return VideoFile(
            file_exists=True,
            filename=file_path.stem,
            file_hash="",
            file_extension=file_path.suffix,
            file_path=file_path,
            file_directory=file_path.parent,
            subs_dir=file_path.parent / "subs",
            tmp_dir=file_path.parent / "tmp_subsearch",
        )

    def _build_empty(self) -> VideoFile:
        return VideoFile(
            file_exists=False,
            filename="",
            file_hash="",
            file_extension="",
            file_path=Path(""),
            file_directory=Path(""),
            subs_dir=Path(""),
            tmp_dir=Path(""),
        )


def get_video_file_data() -> VideoFile:
    return VideoFileResolver(SUPPORTED_FILE_EXTENSIONS).resolve_from_argv()


def get_system_info() -> SystemInfo:
    if getattr(sys, "frozen", False):
        mode = "executable"
        python_version = ""
    else:
        python_version = platform.python_version()
        mode = "interpreter"
    platform_description = platform.platform().lower()
    return SystemInfo(platform_description, mode, python_version, __version__)


def get_windows_registry_paths() -> WindowsRegistryPaths:
    return WindowsRegistryPaths(
        classes=r"Software\Classes",
        asterisk=r"Software\Classes\*",
        shell=r"Software\Classes\*\shell",
        subsearch=r"Software\Classes\*\shell\Subsearch",
        subsearch_command=r"Software\Classes\*\shell\Subsearch\command",
        long_paths=r"SYSTEM\CurrentControlSet\Control\FileSystem",
    )
