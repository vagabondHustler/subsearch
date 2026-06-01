import cloudscraper
from cloudscraper import CloudScraper
from requests import Response, exceptions
from selectolax.parser import HTMLParser

from subsearch.logging import log


def get_cloudscraper() -> CloudScraper:
    return cloudscraper.create_scraper(browser={"browser": "chrome", "platform": "android", "desktop": False})


def send_request(url: str, scraper: CloudScraper, timeout: tuple[int, int], header=None) -> Response:
    if header is None:
        return scraper.get(url, timeout=timeout)
    return scraper.get(url, timeout=timeout, headers=header)


def parse_scraper_response(response: Response) -> HTMLParser:
    return HTMLParser(response.text)


def request_parsed_response(url: str, timeout: tuple[int, int], header=None) -> HTMLParser | None:
    scraper = get_cloudscraper()
    try:
        response = send_request(url, scraper, timeout=timeout, header=header)
    except exceptions.Timeout as e:
        log.stdout(e, level="warning", print_allowed=False)
        return None
    return parse_scraper_response(response)
