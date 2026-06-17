import functools
import json
import os
from pathlib import Path
from typing import Any

from subsearch.runtime.logging.events import LogEvent
from subsearch.runtime.logging.logger import log


def load_json_data(json_file_path: Path) -> dict[str, Any]:
    log.event(LogEvent.CONFIG_READ, level="debug", filename=json_file_path.name)
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

        log.event(LogEvent.CONFIG_WROTE, level="debug", filename=json_file_path.name)
    except Exception as e:
        log.event(LogEvent.CONFIG_WRITE_FAILED, level="error", filename=json_file_path.name, reason=str(e))
        raise
