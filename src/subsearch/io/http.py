from curl_cffi import requests
from curl_cffi.requests import Response, exceptions
from selectolax.lexbor import LexborHTMLParser

from subsearch.parsing.html_parser import parse_html_response
from subsearch.runtime.logging.logger import log


def get_session() -> requests.Session:
    return requests.Session(impersonate="chrome")


def send_request(url: str, session: requests.Session, timeout: tuple[int, int], header=None) -> Response:
    if header is None:
        return session.get(url, timeout=timeout)
    return session.get(url, timeout=timeout, headers=header)


def request_parsed_response(url: str, timeout: tuple[int, int], header=None) -> LexborHTMLParser | None:
    session = get_session()
    try:
        response = send_request(url, session, timeout=timeout, header=header)
    except exceptions.Timeout as e:
        log.warning(str(e), to_console=False)
        return None
    return parse_html_response(response)
