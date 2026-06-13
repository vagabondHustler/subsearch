import functools
import json
import os
from pathlib import Path
from typing import Any

from subsearch.runtime.logging.logger import log


def load_json_data(json_file_path: Path) -> dict[str, Any]:
    log.debug(f"Read json file from {json_file_path.name}")
    with open(json_file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def load_json_value(json_file_path: Path, key: str) -> Any:
    json_data = load_json_data(json_file_path)
    keys = key.split(".")
    value = functools.reduce(dict.get, keys, json_data)  # type: ignore
    return value


def dump_json_data(json_file_path: Path, json_data: dict) -> None:
    temp_file_path = json_file_path.with_suffix(f"{json_file_path.suffix}.tmp")
    try:
        with open(temp_file_path, "w", encoding="utf-8") as file:
            json.dump(json_data, file, indent=2, ensure_ascii=False)
            file.flush()
            os.fsync(file.fileno())
        os.replace(temp_file_path, json_file_path)

        log.debug(f"Wrote config to {json_file_path.name}")
    except Exception as e:
        log.error(f"Failed to write config to {json_file_path.name}: {e}")
        raise
