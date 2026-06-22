import functools
import json
from pathlib import Path
from typing import Any, cast

from subsearch.runtime.config import FILE_PATHS


@functools.lru_cache(maxsize=None)
def _load_cached(language_data_path: Path) -> dict[str, Any]:
    with open(language_data_path, "r", encoding="utf-8") as file:
        return cast(dict[str, Any], json.load(file))


def load_language_data() -> dict[str, Any]:
    return _load_cached(FILE_PATHS.subtitle_languages)
