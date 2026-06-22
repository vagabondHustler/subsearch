import functools
from typing import Any


def set_nested_value(data: dict, key: str, value: Any | None) -> None:
    keys = key.split(".")
    functools.reduce(dict.get, keys[:-1], data)[keys[-1]] = value  # type: ignore


def insert_nested_value(data: dict, key: str, value: Any | None) -> None:
    keys = key.split(".")
    parent = functools.reduce(lambda node, part: node.setdefault(part, {}), keys[:-1], data)
    parent[keys[-1]] = value


def descend_into(node: Any, key: str) -> Any:
    return node.get(key) if isinstance(node, dict) else None


def read_nested_value(data: dict, key: str) -> Any:
    keys = key.split(".")
    return functools.reduce(descend_into, keys, data)


def delete_nested_value(data: dict, key: str) -> None:
    keys = key.split(".")
    parent = functools.reduce(descend_into, keys[:-1], data)
    if isinstance(parent, dict):
        parent.pop(keys[-1], None)


def changed_leaves(key: str, previous_value: Any, new_value: Any) -> list[tuple[str, Any, Any]]:
    if isinstance(previous_value, dict) and isinstance(new_value, dict):
        leaves: list[tuple[str, Any, Any]] = []
        for nested_key in new_value:
            leaves.extend(changed_leaves(f"{key}.{nested_key}", previous_value.get(nested_key), new_value[nested_key]))
        return leaves
    if previous_value == new_value:
        return []
    return [(key, previous_value, new_value)]


def get_keys_recursively(dictionary: dict, prefix: str = "", keys: list[str] | None = None) -> list[str]:
    if keys is None:
        keys = []

    if isinstance(dictionary, dict):
        for key in dictionary:
            full_key = f"{prefix}.{key}" if prefix else key
            keys.append(full_key)
            get_keys_recursively(dictionary[key], full_key, keys)

    return keys
