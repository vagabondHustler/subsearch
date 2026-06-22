import pytest

from subsearch.io import app_updater


class FakeResponse:
    def __init__(self, status_code: int, url: str = "", text: str = "") -> None:
        self.status_code = status_code
        self.url = url
        self.text = text


class FakeSession:
    def __init__(self, response: FakeResponse) -> None:
        self.response = response
        self.urls: list[str] = []

    def get(self, url: str, **_kwargs) -> FakeResponse:
        self.urls.append(url)
        return self.response


def test_fetch_latest_release_scrapes_github_release_page(monkeypatch) -> None:
    response = FakeResponse(
        status_code=200,
        url="https://github.com/vagabondHustler/subsearch/releases/tag/3.1.0",
        text="""
            <article>
              <div class="markdown-body"><h2>Added</h2><p>Automatic updates</p></div>
            </article>
        """,
    )
    session = FakeSession(response)
    monkeypatch.setattr(app_updater, "get_session", lambda: session)

    release = app_updater.fetch_latest_release()

    assert session.urls == [app_updater.LATEST_RELEASE_PAGE]
    assert release.version == "3.1.0"
    assert release.changelog == "Added\nAutomatic updates"


def test_fetch_latest_release_rejects_a_page_without_a_tag(monkeypatch) -> None:
    response = FakeResponse(status_code=200, url="https://github.com/vagabondHustler/subsearch/releases")
    monkeypatch.setattr(app_updater, "get_session", lambda: FakeSession(response))

    with pytest.raises(app_updater.VersionUnavailable, match="release tag"):
        app_updater.fetch_latest_release()


def test_check_for_update_uses_the_scraped_release_version(monkeypatch) -> None:
    release = app_updater.GitHubRelease(version="3.1.0", changelog="Changes")
    monkeypatch.setattr(app_updater, "VERSION", "3.0.0")
    monkeypatch.setattr(app_updater, "fetch_latest_release", lambda: release)

    availability = app_updater.check_for_update()

    assert availability.current_version == "3.0.0"
    assert availability.latest_version == "3.1.0"
    assert availability.update_available is True
    assert availability.changelog == "Changes"


def test_installer_url_uses_the_same_release_tag() -> None:
    assert app_updater.installer_url("3.1.0") == (
        "https://github.com/vagabondHustler/subsearch/releases/download/3.1.0/Subsearch-3.1.0-win64.msi"
    )
