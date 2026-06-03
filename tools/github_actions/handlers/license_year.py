import re
from datetime import datetime, timezone
from pathlib import Path

COPYRIGHT_PATTERN = re.compile(r"Copyright \(C\) (\d{4})(?:-\d{4})? vagabondHustler")


def current_year() -> int:
    return datetime.now(timezone.utc).year


def renew_copyright_year(license_text: str, year: int) -> str:
    def replace(match: re.Match[str]) -> str:
        start_year = int(match.group(1))
        span = f"{start_year}-{year}" if year > start_year else f"{start_year}"
        return f"Copyright (C) {span} vagabondHustler"

    return COPYRIGHT_PATTERN.sub(replace, license_text, count=1)


def update_license_file(license_path: Path, year: int) -> bool:
    original = license_path.read_text(encoding="utf-8")
    renewed = renew_copyright_year(original, year)
    if renewed == original:
        return False
    license_path.write_text(renewed, encoding="utf-8", newline="\n")
    return True
