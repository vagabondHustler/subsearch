from dataclasses import dataclass, field
from enum import Enum, IntEnum
from typing import Any


class SubtitleStatus(Enum):
    FILTERED_OUT = "filtered_out"
    BELOW_THRESHOLD = "below_threshold"
    ACCEPTED = "accepted"
    AUTO_DOWNLOADED = "auto_downloaded"
    MANUALLY_DOWNLOADED = "manually_downloaded"
    DOWNLOAD_FAILED = "download_failed"


@dataclass(slots=True)
class Subtitle:
    token_result: int
    provider_name: str
    subtitle_name: str
    download_url: str
    request_data: dict[str, Any]
    download_headers: dict[str, str] = field(default_factory=dict)
    status: SubtitleStatus = SubtitleStatus.BELOW_THRESHOLD
    hash_match: bool = False


@dataclass(slots=True)
class SearchOutcome:
    subtitles: list[Subtitle]
    skipped_providers: list[str]


class MatchTier(IntEnum):
    C = 0
    B = 1
    A = 2
    S = 3


def classify_match_tier(hash_match: bool, percentage_result: int, accept_threshold: int) -> MatchTier:
    if hash_match:
        return MatchTier.S
    if percentage_result == 100:
        return MatchTier.A
    if percentage_result >= accept_threshold:
        return MatchTier.B
    return MatchTier.C
