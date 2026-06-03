import subprocess
import sys
from pathlib import Path

# Invoked as a module rather than the `cz` console script so the current working
# directory is on sys.path and the SubsearchCz plugin (in tools/) is importable.
_COMMITIZEN = [sys.executable, "-m", "commitizen"]
_TAG_TO_CREATE_PREFIX = "tag to create:"


def current_version() -> str:
    completed = subprocess.run([*_COMMITIZEN, "version", "--project"], check=True, capture_output=True, text=True)
    return completed.stdout.strip()


def bump_version() -> None:
    # cz bump exits non-zero with NoneIncrementError when no commits warrant a
    # release; the caller detects that no-op by comparing versions, so the
    # failure is swallowed here rather than treated as an error.
    subprocess.run([*_COMMITIZEN, "bump", "--yes"])


def predicted_next_version() -> str | None:
    completed = subprocess.run([*_COMMITIZEN, "bump", "--dry-run", "--yes"], capture_output=True, text=True)
    if completed.returncode != 0:
        return None
    for line in completed.stdout.splitlines():
        if line.strip().startswith(_TAG_TO_CREATE_PREFIX):
            return line.split(_TAG_TO_CREATE_PREFIX, 1)[1].strip()
    return None


def render_changelog_for_tag(tag: str, file_name: Path) -> None:
    subprocess.run([*_COMMITIZEN, "changelog", tag, "--file-name", str(file_name)], check=True)


def render_unreleased_changelog(unreleased_version: str, file_name: Path) -> None:
    subprocess.run(
        [*_COMMITIZEN, "changelog", "--unreleased-version", unreleased_version, "--file-name", str(file_name)],
        check=True,
    )
