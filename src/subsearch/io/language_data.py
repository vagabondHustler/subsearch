import functools
from pathlib import Path
from typing import Any

import toml

from subsearch.runtime.config.constants import FILE_PATHS


@functools.lru_cache(maxsize=None)
def _load_cached(language_data_path: Path) -> dict[str, Any]:
    with open(language_data_path, "r") as file:
        return toml.load(file)


def load_language_data() -> dict[str, Any]:
    return _load_cached(FILE_PATHS.subtitle_languages)
