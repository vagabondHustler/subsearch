from curl_cffi.requests import exceptions

from subsearch.io import http


class _FakeResponse:
    def __init__(self, status_code: int) -> None:
        self.status_code = status_code


def _capture_events(monkeypatch) -> list[tuple[str, dict]]:
    captured: list[tuple[str, dict]] = []
    monkeypatch.setattr(http.log, "event", lambda key, **values: captured.append((key, values)))
    return captured


def test_request_failed_returns_none_and_logs(monkeypatch) -> None:
    captured = _capture_events(monkeypatch)

    def raise_connection_error(*args, **kwargs):
        raise exceptions.ConnectionError("boom")

    monkeypatch.setattr(http, "send_request", raise_connection_error)

    result = http.request_parsed_response("https://example.test", timeout=(1, 1))

    assert result is None
    assert any(key == "http.request_failed" for key, _ in captured)


def test_bad_status_returns_none_and_logs(monkeypatch) -> None:
    captured = _capture_events(monkeypatch)
    monkeypatch.setattr(http, "send_request", lambda *args, **kwargs: _FakeResponse(503))

    result = http.request_parsed_response("https://example.test", timeout=(1, 1))

    assert result is None
    assert any(key == "http.bad_status" and values["status_code"] == 503 for key, values in captured)


def test_success_parses_response(monkeypatch) -> None:
    monkeypatch.setattr(http, "send_request", lambda *args, **kwargs: _FakeResponse(200))
    monkeypatch.setattr(http, "parse_html_response", lambda response: "parsed")

    assert http.request_parsed_response("https://example.test", timeout=(1, 1)) == "parsed"
