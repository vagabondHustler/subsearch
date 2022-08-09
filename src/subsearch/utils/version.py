import json

from . import local_paths


def read_data(config_file: str) -> dict:
    with open(config_file, encoding="utf-8") as file:
        data = json.load(file)
        version = data["version"]
        return version


def current() -> str:
    c_version = read_data(local_paths.get_path("data", "version.json"))
    return c_version
