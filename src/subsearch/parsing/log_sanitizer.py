import getpass
import os
import re
from pathlib import Path

from subsearch.runtime.constants import COMPUTER_NAME, FILE_PATHS, GUID

REDACTED = "[redacted]"

IP_ADDRESS_PATTERN = re.compile(r"\b\d{1,3}(?:\.\d{1,3}){3}\b")
EMAIL_PATTERN = re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b")
API_KEY_PATTERN = re.compile(r"\bsk_[A-Za-z0-9_-]+", re.IGNORECASE)


def _username_candidates() -> list[str]:
    candidates = [getpass.getuser(), os.environ.get("USERNAME", ""), Path.home().name]
    return sorted({name for name in candidates if name}, key=len, reverse=True)


def sanitize(text: str) -> str:
    text = API_KEY_PATTERN.sub(REDACTED, text)
    text = EMAIL_PATTERN.sub(REDACTED, text)
    if GUID:
        text = text.replace(GUID, REDACTED)
    if COMPUTER_NAME:
        text = re.sub(re.escape(COMPUTER_NAME), REDACTED, text, flags=re.IGNORECASE)
    for username in _username_candidates():
        text = re.sub(re.escape(username), REDACTED, text, flags=re.IGNORECASE)
    return IP_ADDRESS_PATTERN.sub(REDACTED, text)


def read_sanitized_log() -> str:
    raw_log = FILE_PATHS.log.read_text(encoding="utf-8", errors="replace")
    return sanitize(raw_log)
