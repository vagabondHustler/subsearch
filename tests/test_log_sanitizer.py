import re

from subsearch.runtime.logging import log_sanitizer


def test_sanitize_redacts_api_key() -> None:
    assert "sk_" not in log_sanitizer.sanitize("key=sk_abc123DEF")


def test_sanitize_redacts_email() -> None:
    assert "@" not in log_sanitizer.sanitize("contact user.name@example.org now")


def test_sanitize_redacts_ip_address() -> None:
    assert "192.168.1.1" not in log_sanitizer.sanitize("host 192.168.1.1 down")


def test_sanitize_identity_matches_whole_word_only(monkeypatch) -> None:
    pattern = re.compile(r"\bdev\b", re.IGNORECASE)
    monkeypatch.setattr(log_sanitizer, "_IDENTITY_PATTERNS", [pattern])
    sanitized = log_sanitizer.sanitize("development of the dev branch")
    assert "development" in sanitized
    assert " dev " not in sanitized


def test_sanitize_identity_redacts_username_in_path(monkeypatch) -> None:
    pattern = re.compile(r"\bdev\b", re.IGNORECASE)
    monkeypatch.setattr(log_sanitizer, "_IDENTITY_PATTERNS", [pattern])
    sanitized = log_sanitizer.sanitize(r"C:\Users\dev\AppData\Local")
    assert "dev" not in sanitized.replace(log_sanitizer.REDACTED, "")
