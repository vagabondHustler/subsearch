import dataclasses
import getpass
import os
import re
from pathlib import Path

from subsearch.runtime.constants import COMPUTER_NAME, FILE_PATHS, GUID
from subsearch.runtime.model import DataclassInstance

REDACTED = "[redacted]"

IP_ADDRESS_PATTERN = re.compile(r"\b\d{1,3}(?:\.\d{1,3}){3}\b")
EMAIL_PATTERN = re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b")
API_KEY_PATTERN = re.compile(r"\bsk_[A-Za-z0-9_-]+", re.IGNORECASE)

SECRET_FIELDS = {"subsource_api_key"}


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


def _secret_field_status(value: object) -> str:
    api_key = str(value)
    if not api_key:
        return "<not set>"
    return "<valid key>" if re.match(r"^sk_[0-9a-f]+$", api_key) else "<invalid key>"


def dataclass_lines(instance: DataclassInstance, banner_template: str) -> list[str]:
    if not dataclasses.is_dataclass(instance):
        raise ValueError("Input is not a dataclass instance.")
    lines = [banner_template.format(title=instance.__class__.__name__)]
    for field in dataclasses.fields(instance):
        value = getattr(instance, field.name)
        if field.name in SECRET_FIELDS:
            value = _secret_field_status(value)
        padding = " " * (30 - len(field.name))
        lines.append(f"{field.name}:{padding}{value}")
    return lines


CRASH_PATTERN = re.compile(r"\b(ERROR|Traceback|Exception)\b")

SESSION_SEPARATOR = "\x1c"


def _sessions(raw_log: str) -> list[str]:
    return [block.strip() for block in raw_log.split(SESSION_SEPARATOR) if block.strip()]


def sessions_with_crash(raw_log: str) -> str:
    sessions = _sessions(raw_log)
    crashed = [session for session in sessions if CRASH_PATTERN.search(session)]
    if crashed:
        return f"\n\n{SESSION_SEPARATOR}\n\n".join(crashed)
    return sessions[-1] if sessions else raw_log


def read_sanitized_log() -> str:
    raw_log = FILE_PATHS.log.read_text(encoding="utf-8", errors="replace")
    return sanitize(raw_log)


def read_sanitized_crash_sessions() -> str:
    raw_log = FILE_PATHS.log.read_text(encoding="utf-8", errors="replace")
    return sanitize(sessions_with_crash(raw_log))
