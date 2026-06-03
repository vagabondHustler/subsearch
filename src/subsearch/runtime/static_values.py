import socket

from subsearch.runtime.guid import __guid__
from subsearch.runtime.version import __version__


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
    providers = ["opensubtitles", "yifysubtitles_site", "subsource_site"]
    return providers


def get_computer_name() -> str:
    return socket.gethostname()


def get_app_version() -> str:
    return str(__version__)


def get_guid() -> str:
    return str(__guid__)
