import getpass
import os
import re
from pathlib import Path

from subsearch.runtime.config import COMPUTER_NAME, FILE_PATHS, GUID
from subsearch.runtime.recorder.config import SESSION_SEPARATOR

# matches IPv4 addresses e.g. "192.168.1.1" matches, "1234.1.1.1" does not
IP_ADDRESS_PATTERN = re.compile(r"\b\d{1,3}(?:\.\d{1,3}){3}\b")
# matches email addresses e.g. "user.name+tag@sub.domain.org"
EMAIL_PATTERN = re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b")
# matches subsource API keys e.g. "sk_AbcDef123", case-insensitive
API_KEY_PATTERN = re.compile(r"\bsk_[A-Za-z0-9_-]+", re.IGNORECASE)

REDACTED = "***"
_REDACTED_USERNAME = "USERNAME"


def _username_candidates() -> list[str]:
    candidates = [getpass.getuser(), os.environ.get("USERNAME", ""), Path.home().name]
    return sorted({name for name in candidates if name}, key=len, reverse=True)


def _identity_patterns() -> list[re.Pattern[str]]:
    names = _username_candidates()
    if COMPUTER_NAME:
        names.append(COMPUTER_NAME)
    # matches a username or computer name as a whole word; backslashes count as word boundaries so paths still match
    return [re.compile(rf"\b{re.escape(name)}\b", re.IGNORECASE) for name in names]


_IDENTITY_PATTERNS = _identity_patterns()


def sanitize(text: str) -> str:
    text = API_KEY_PATTERN.sub(REDACTED, text)
    text = EMAIL_PATTERN.sub(REDACTED, text)
    if GUID:
        text = text.replace(GUID, REDACTED)
    for pattern in _IDENTITY_PATTERNS:
        text = pattern.sub(_REDACTED_USERNAME, text)
    return IP_ADDRESS_PATTERN.sub(REDACTED, text)


def _sessions(raw_log: str) -> list[str]:
    return [block.strip() for block in raw_log.split(SESSION_SEPARATOR) if block.strip()]


def _current_session(raw_log: str) -> str:
    sessions = _sessions(raw_log)
    return sessions[-1] if sessions else raw_log


def read_sanitized_crash_sessions() -> str:
    if FILE_PATHS.crash.exists():
        crash_log = FILE_PATHS.crash.read_text(encoding="utf-8", errors="replace")
        if crash_log.strip():
            return sanitize(crash_log)
    raw_log = FILE_PATHS.log.read_text(encoding="utf-8", errors="replace")
    return sanitize(_current_session(raw_log))
