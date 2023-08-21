import platform
import socket
import sys
import tempfile
from itertools import product
from pathlib import Path
from typing import Any, no_type_check

from subsearch.data import __version__
from subsearch.data.data_classes import (
    AppPaths,
    FilePaths,
    SystemInfo,
    VideoFile,
    WindowsRegistryPaths,
)


def get_app_paths() -> AppPaths:
    app_home = Path(__file__).resolve().parent.parent
    return AppPaths(
        home=app_home,
        data=app_home / "data",
        gui=app_home / "gui",
        gui_assets=app_home / "gui" / "resources" / "assets",
        gui_styles=app_home / "gui" / "resources" / "styles",
        providers=app_home / "providers",
        utils=app_home / "utils",
        tmp_dir=Path(tempfile.gettempdir()) / f"tmp_subsearch",
        appdata_subsearch=Path.home() / "AppData" / "Local" / "Subsearch",
    )


def get_file_paths() -> FilePaths:
    app_home = Path(__file__).resolve().parent.parent
    return FilePaths(
        log=Path.home() / "AppData" / "Local" / "Subsearch" / "log.log",
        config=Path.home() / "AppData" / "Local" / "Subsearch" / "config.toml",
        language_data=app_home / "data" / "language_data.toml",
    )


def get_default_app_config() -> dict[str, Any]:
    file_extensions = dict.fromkeys(get_supported_file_ext(), True)
    providers = dict.fromkeys(get_supported_providers(), True)
    config = {
        "subtitle_filters": {
            "language": "english",
            "accept_threshold": 90,
            "hearing_impaired": True,
            "non_hearing_impaired": True,
            "only_foreign_parts": False,
        },
        "gui": {
            "context_menu": True,
            "context_menu_icon": True,
            "system_tray": True,
            "summary_notification": False,
            "show_terminal": False,
        },
        "subtitle_post_processing": {
            "rename": True,
            "move_best": True,
            "move_all": False,
            "target_path": ".",
            "path_resolution": "relative",
        },
        "file_extensions": file_extensions,
        "providers": providers,
        "misc": {
            "manual_download_on_fail": True,
            "multithreading": True,
            "single_instance": True,
        },
    }
    return config


@no_type_check
def get_video_file_data() -> VideoFile:
    file_exist = False
    supported_exts = get_supported_file_ext()
    for i in product(supported_exts, sys.argv):
        if i[1].endswith(i[0]) and str(i[1])[i[1].rfind("\\") :].startswith("\\"):
            file_path = Path(i[1])
            file_directory = file_path.parent
            tmp_dir = file_directory / "tmp_subsearch"
            subs_dir = file_directory / "subs"
            file_name = file_path.stem
            file_ext = file_path.suffix
            file_exist = True
            file_hash = ""
            break

    if file_exist:
        video_file = VideoFile(
            filename=file_name,
            file_hash=file_hash,
            file_extension=file_ext,
            file_path=file_path,
            file_directory=file_directory,
            subs_dir=subs_dir,
            tmp_dir=tmp_dir,
        )
        return video_file


def get_system_info() -> SystemInfo:
    if getattr(sys, "frozen", False):
        mode = "executable"
        python = ""
    else:
        python = platform.python_version()
        mode = "interpreter"
    platform_ = platform.platform().lower()

    return SystemInfo(platform_, mode, python, __version__)


def get_supported_file_ext() -> list[str]:
    exts = [
        "avi",
        "mp4",
        "mkv",
        "mpg",
        "mpeg",
        "mov",
        "rm",
        "vob",
        "wmv",
        "flv",
        "3gp",
        "3g2",
        "swf",
        "mswmm",
    ]
    return exts


def get_supported_providers() -> list[str]:
    providers = ["opensubtitles_site", "opensubtitles_hash", "subscene_site", "yifysubtitles_site"]
    return providers


def get_windows_registry_paths() -> WindowsRegistryPaths:
    registry_paths = WindowsRegistryPaths(
        classes=r"Software\Classes",
        asterisk=r"Software\Classes\*",
        shell=r"Software\Classes\*\shell",
        subsearch=r"Software\Classes\*\shell\Subsearch",
        subsearch_command=r"Software\Classes\*\shell\Subsearch\command",
    )
    return registry_paths


def get_computer_name() -> str:
    return socket.gethostname()
