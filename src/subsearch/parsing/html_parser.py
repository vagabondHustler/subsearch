from curl_cffi.requests import Response
from selectolax.lexbor import LexborHTMLParser


def parse_html_response(response: Response) -> LexborHTMLParser:
    return LexborHTMLParser(response.text)
