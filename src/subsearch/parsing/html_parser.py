from curl_cffi.requests import Response
from selectolax.parser import HTMLParser


def parse_html_response(response: Response) -> HTMLParser:
    return HTMLParser(response.text)
