from dataclasses import dataclass
from enum import Enum


class ProviderDiagnosticStatus(Enum):
    OK = "ok"
    NO_RESPONSE = "no_response"
    STRUCTURE_INVALID = "structure_invalid"


@dataclass(slots=True)
class ProviderResult:
    provider_name: str
    diagnostic_status: ProviderDiagnosticStatus
    subtitles_found: int


@dataclass(slots=True)
class ProviderApiLimit:
    opensubtitles: int
    yifysubtitles: int
    subsource: int
