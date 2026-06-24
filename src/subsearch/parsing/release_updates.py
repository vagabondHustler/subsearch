import re
from dataclasses import dataclass
from urllib.parse import unquote, urlparse

from packaging.version import InvalidVersion, Version
from selectolax.lexbor import LexborHTMLParser

from subsearch.io import app_updater
from subsearch.runtime.config import VERSION

_RELEASE_TAG_PATTERN = re.compile(
    r"/releases/tag/([^/?#]+)$"
)  # matches the release tag at the end of a GitHub release URL


@dataclass(frozen=True, slots=True)
class GitHubRelease:
    version: str
    changelog: str


@dataclass(frozen=True, slots=True)
class UpdateAvailability:
    current_version: str
    latest_version: str
    update_available: bool
    is_prerelease: bool
    changelog: str


class VersionUnavailable(Exception): ...


def parse_release_version(release_url: str) -> str:
    release_path = urlparse(release_url).path
    match = _RELEASE_TAG_PATTERN.search(release_path)
    if match is None:
        raise VersionUnavailable("Could not find a release tag on GitHub")
    version = unquote(match.group(1))
    try:
        Version(version)
    except InvalidVersion as error:
        raise VersionUnavailable(f"GitHub returned an invalid release version: {version}") from error
    return version


def parse_release_changelog(release_page: str) -> str:
    changelog = LexborHTMLParser(release_page).css_first(".markdown-body")
    return changelog.text(separator="\n", strip=True) if changelog is not None else ""


def parse_github_release(release_url: str, release_page: str) -> GitHubRelease:
    return GitHubRelease(version=parse_release_version(release_url), changelog=parse_release_changelog(release_page))


def fetch_latest_release() -> GitHubRelease:
    try:
        page = app_updater.fetch_latest_release_page()
    except app_updater.ReleasePageError as error:
        raise VersionUnavailable(str(error)) from error
    return parse_github_release(page.final_url, page.html)


def check_for_update() -> UpdateAvailability:
    return evaluate_update(VERSION, fetch_latest_release())


def evaluate_update(current_version: str, latest_release: GitHubRelease) -> UpdateAvailability:
    update_available = Version(current_version) < Version(latest_release.version)
    return UpdateAvailability(
        current_version=current_version,
        latest_version=latest_release.version,
        update_available=update_available,
        is_prerelease=update_available and Version(latest_release.version).is_prerelease,
        changelog=latest_release.changelog,
    )
