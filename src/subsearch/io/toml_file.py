import functools
import os
from pathlib import Path
from typing import Any

import toml

from subsearch.runtime.logging.logger import log


def load_toml_data(toml_file_path: Path) -> dict[str, Any]:
    log.debug(f"Read toml file from {toml_file_path.name}")
    with open(toml_file_path, "r") as f:
        return toml.load(f)


def load_toml_value(toml_file_path: Path, key: str) -> Any:
    toml_data = load_toml_data(toml_file_path)
    keys = key.split(".")
    value = functools.reduce(dict.get, keys, toml_data)  # type: ignore
    return value


def dump_toml_data(toml_file_path: Path, toml_data: dict) -> None:
    temp_file_path = toml_file_path.with_suffix(f"{toml_file_path.suffix}.tmp")
    try:
        with open(temp_file_path, "w") as file:
            toml.dump(toml_data, file)
            file.flush()
            os.fsync(file.fileno())
        os.replace(temp_file_path, toml_file_path)

        log.debug(f"Wrote config to {toml_file_path.name}")
    except Exception as e:
        log.error(f"Failed to write config to {toml_file_path.name}: {e}")
        raise
