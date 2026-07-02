from dataclasses import dataclass, field
from enum import Enum, IntEnum
from typing import Any
from uuid import uuid4


class SubtitleStatus(Enum):
    FILTERED_OUT = "filtered_out"
    BELOW_THRESHOLD = "below_threshold"
    ACCEPTED = "accepted"
    AUTO_DOWNLOAD = "auto_download"
    MANUAL_DOWNLOAD = "manual_download"
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
    download_count: int = 0
    subtitle_id: str = field(default_factory=lambda: uuid4().hex[:5])


@dataclass(slots=True)
class SearchOutcome:
    subtitles: list[Subtitle]
    skipped_providers: list[str]


@dataclass(slots=True)
class WorkspaceOutcome:
    downloaded: list[Subtitle]
    placed_best_next_to_video: bool = False


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
