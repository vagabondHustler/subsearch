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


def test_fetch_latest_release_page_returns_the_final_url_and_html(monkeypatch) -> None:
    response = FakeResponse(status_code=200, url="https://example.test/releases/tag/3.1.0", text="<html>body</html>")
    session = FakeSession(response)
    monkeypatch.setattr(app_updater, "get_session", lambda: session)

    page = app_updater.fetch_latest_release_page()

    assert session.urls == [app_updater.LATEST_RELEASE_PAGE]
    assert page.final_url == "https://example.test/releases/tag/3.1.0"
    assert page.html == "<html>body</html>"


def test_fetch_latest_release_page_raises_on_a_non_success_status(monkeypatch) -> None:
    monkeypatch.setattr(app_updater, "get_session", lambda: FakeSession(FakeResponse(status_code=404)))

    with pytest.raises(app_updater.ReleasePageError, match="HTTP 404"):
        app_updater.fetch_latest_release_page()


def test_installer_url_uses_the_same_release_tag() -> None:
    assert app_updater.installer_url("3.1.0") == (
        "https://github.com/vagabondHustler/subsearch/releases/download/3.1.0/Subsearch-3.1.0-win64.msi"
    )
