from curl_cffi.requests import exceptions

from subsearch.io import http


class _FakeResponse:
    def __init__(self, status_code: int) -> None:
        self.status_code = status_code


def test_request_failed_returns_none(monkeypatch) -> None:
    def raise_connection_error(*args, **kwargs):
        raise exceptions.ConnectionError("boom")

    monkeypatch.setattr(http, "send_request", raise_connection_error)

    assert http.request_parsed_response("https://example.test", timeout=(1, 1)) is None


def test_bad_status_returns_none(monkeypatch) -> None:
    monkeypatch.setattr(http, "send_request", lambda *args, **kwargs: _FakeResponse(503))

    assert http.request_parsed_response("https://example.test", timeout=(1, 1)) is None


def test_success_parses_response(monkeypatch) -> None:
    monkeypatch.setattr(http, "send_request", lambda *args, **kwargs: _FakeResponse(200))
    monkeypatch.setattr(http, "parse_html_response", lambda response: "parsed")

    assert http.request_parsed_response("https://example.test", timeout=(1, 1)) == "parsed"
