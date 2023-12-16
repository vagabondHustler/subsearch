import functools
import json
from pathlib import Path
from typing import Any


def load_json_value(json_file_path: Path, key: str) -> Any:
    """
    Load a value from a JSON file based on a specified key.

    Args:
        json_file_path (Path): The path to the JSON file.
        key (str): The key to retrieve the value.

    Returns:
        Any: The value associated with the specified key.
    """
    with open(json_file_path, "r") as f:
        json_data = json.load(f)
        keys = key.split(".")
        value = functools.reduce(dict.get, keys, json_data)  # type: ignore
        return value


def update_json_key(json_file_path: Path, key: str, value: Any | None) -> None:
    """
    Update a key in a JSON file with a new value.

    Args:
        json_file_path (Path): The path to the JSON file.
        key (str): The key to be updated.
        value (Any | None): The new value for the specified key. If None, the key will be removed.
    """
    with open(json_file_path, "r") as f:
        json_data = json.load(f)
        keys = key.split(".")
        functools.reduce(dict.get, keys[:-1], json_data)[keys[-1]] = value  # type: ignore

    with open(json_file_path, "w") as f:
        json.dump(json_data, f, indent=2)
