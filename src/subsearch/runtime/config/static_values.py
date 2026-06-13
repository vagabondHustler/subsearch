import socket

from subsearch.runtime.config.guid import __guid__
from subsearch.runtime.config.version import __version__

SUPPORTED_FILE_EXTENSIONS: list[str] = [
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

DEFAULT_TOKEN_WEIGHTS: dict[str, float] = {
    "title": 75,
    "group": 5,
    "source": 20,
}

DEFAULT_TOKEN_MULTIPLIERS: dict[str, float] = {
    "year": 0.1,
    "season_episode": 0.1,
    "edition": 0.1,
}

SUPPORTED_PROVIDERS: list[str] = ["opensubtitles", "yifysubtitles_site", "subsource_site"]

HEALTH_TRACKED_PROVIDERS: list[str] = ["imdb", "opensubtitles", "yifysubtitles", "subsource"]

COMPUTER_NAME: str = socket.gethostname()

APP_VERSION: str = str(__version__)

APP_GUID: str = str(__guid__)
