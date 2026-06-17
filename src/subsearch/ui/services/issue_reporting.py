import webbrowser
from urllib.parse import urlencode

from subsearch.runtime.config import DEVICE_INFO, SEARCH_SUBJECT, VERSION

ISSUE_TEMPLATE_URL = "https://github.com/vagabondHustler/subsearch/issues/new"
NO_VIDEO_FILE = "none (running in configure mode, no video file was opened)"


def _media_filename() -> str:
    if SEARCH_SUBJECT.file_exists:
        return f"{SEARCH_SUBJECT.search_term}{SEARCH_SUBJECT.file_extension}"
    return NO_VIDEO_FILE


def _build_prefilled_issue_body() -> str:
    return (
        "#### Description:\n\n"
        "A clear description of the issue and when it occurs.\n\n"
        "#### Steps to reproduce:\n\n"
        "The steps required to trigger the behaviour.\n\n"
        "#### Environment:\n\n"
        f"- OS: {DEVICE_INFO.platform}\n"
        f"- Python version: {DEVICE_INFO.python}\n"
        f"- Filename: {_media_filename()}\n"
        f"- App version: {VERSION}\n\n"
        "#### Additional context:\n\n"
        "Any other details, logs, or screenshots that may help.\n"
    )


def open_bug_report() -> None:
    query = urlencode(
        {"template": "bug_report.md", "title": "", "labels": "bug", "body": _build_prefilled_issue_body()}
    )
    webbrowser.open(f"{ISSUE_TEMPLATE_URL}?{query}")
