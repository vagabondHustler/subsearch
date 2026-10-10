from dataclasses import dataclass
from enum import Enum


class AppMode(Enum):
    SETTINGS = "settings"
    SEARCH_MANUAL = "search_manual"
    SEARCH_AUTOMATIC = "search_automatic"


@dataclass(slots=True, frozen=True)
class SystemInfo:
    platform: str
    mode: str
    python: str
    subsearch: str
