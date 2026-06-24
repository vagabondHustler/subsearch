import pytest

from subsearch.io.app_updater import ReleasePage, ReleasePageError
from subsearch.parsing import release_updates


def test_fetch_latest_release_scrapes_the_release_page(monkeypatch) -> None:
    page = ReleasePage(
        final_url="https://github.com/vagabondHustler/subsearch/releases/tag/3.1.0",
        html="""
            <article>
              <div class="markdown-body"><h2>Added</h2><p>Automatic updates</p></div>
            </article>
        """,
    )
    monkeypatch.setattr(release_updates.app_updater, "fetch_latest_release_page", lambda: page)

    release = release_updates.fetch_latest_release()

    assert release.version == "3.1.0"
    assert release.changelog == "Added\nAutomatic updates"


def test_fetch_latest_release_rejects_a_page_without_a_tag(monkeypatch) -> None:
    page = ReleasePage(final_url="https://github.com/vagabondHustler/subsearch/releases", html="")
    monkeypatch.setattr(release_updates.app_updater, "fetch_latest_release_page", lambda: page)

    with pytest.raises(release_updates.VersionUnavailable, match="release tag"):
        release_updates.fetch_latest_release()


def test_fetch_latest_release_wraps_io_errors(monkeypatch) -> None:
    def raise_page_error() -> ReleasePage:
        raise ReleasePageError("Could not reach GitHub")

    monkeypatch.setattr(release_updates.app_updater, "fetch_latest_release_page", raise_page_error)

    with pytest.raises(release_updates.VersionUnavailable, match="Could not reach GitHub"):
        release_updates.fetch_latest_release()


def test_check_for_update_uses_the_scraped_release_version(monkeypatch) -> None:
    release = release_updates.GitHubRelease(version="3.1.0", changelog="Changes")
    monkeypatch.setattr(release_updates, "VERSION", "3.0.0")
    monkeypatch.setattr(release_updates, "fetch_latest_release", lambda: release)

    availability = release_updates.check_for_update()

    assert availability.current_version == "3.0.0"
    assert availability.latest_version == "3.1.0"
    assert availability.update_available is True
    assert availability.changelog == "Changes"
