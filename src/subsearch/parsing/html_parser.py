from typing import TYPE_CHECKING

from selectolax.lexbor import LexborHTMLParser

if TYPE_CHECKING:
    from curl_cffi.requests import Response


def parse_html_response(response: "Response") -> LexborHTMLParser:
    return LexborHTMLParser(response.text)
