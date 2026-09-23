from typing import TYPE_CHECKING

from selectolax.lexbor import LexborHTMLParser

from subsearch.parsing.html_parser import parse_html_response
from subsearch.runtime.recorder import LogLevel, capture

if TYPE_CHECKING:
    from curl_cffi import requests
    from curl_cffi.requests import Response


def get_session() -> "requests.Session":
    from curl_cffi import requests

    return requests.Session(impersonate="chrome")


def send_request(
    url: str, session: "requests.Session", timeout: tuple[int, int], header: dict[str, str] | None = None
) -> "Response":
    if header is None:
        return session.get(url, timeout=timeout)
    return session.get(url, timeout=timeout, headers=header)


def request_parsed_response(
    url: str, timeout: tuple[int, int], header: dict[str, str] | None = None
) -> LexborHTMLParser | None:
    from curl_cffi.requests import exceptions

    session = get_session()
    try:
        response = send_request(url, session, timeout=timeout, header=header)
    except exceptions.RequestException as request_error:
        capture(f"Request failed for {url}: {request_error}", level=LogLevel.WARNING)
        return None
    if not 200 <= response.status_code < 300:
        capture(f"Request to {url} returned status {response.status_code}", level=LogLevel.WARNING)
        return None
    return parse_html_response(response)


def request_parsed_post(url: str, data: dict[str, str], timeout: tuple[int, int]) -> LexborHTMLParser | None:
    from curl_cffi.requests import exceptions

    session = get_session()
    try:
        response = session.post(url, data=data, timeout=timeout)
    except exceptions.RequestException as request_error:
        capture(f"Request failed for {url}: {request_error}", level=LogLevel.WARNING)
        return None
    if not 200 <= response.status_code < 300:
        capture(f"Request to {url} returned status {response.status_code}", level=LogLevel.WARNING)
        return None
    return parse_html_response(response)
