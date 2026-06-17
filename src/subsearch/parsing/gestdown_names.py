import re

from subsearch.parsing import release_parser

# matches a trailing parenthetical qualifier like "(US)", "(uk)" or "(2017)" at the end of a show name
_TRAILING_QUALIFIER_PATTERN = re.compile(r"\s*\([^)]*\)\s*$")
# matches runs of separators (dash, dot, colon) left in a show name after punctuation normalization
_SEPARATOR_RUN_PATTERN = re.compile(r"[-.:]+")


def normalize_show_name(name: str) -> str:
    normalized = release_parser.normalize_typed_punctuation(name.lower())
    normalized = _TRAILING_QUALIFIER_PATTERN.sub("", normalized)
    normalized = _SEPARATOR_RUN_PATTERN.sub(" ", normalized)
    return " ".join(normalized.split())
