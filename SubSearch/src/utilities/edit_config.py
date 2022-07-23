import ctypes
import json
import os

from src.utilities.local_paths import root_directory
from src.utilities.fetch_config import get


# update config.json
def update_json(
    key: str, value: str or int, directory: str = "data", file: str = "config.json"
) -> None:
    with open(root_directory(directory, file), "r+", encoding="utf-8") as f:
        data = json.load(f)
        data[key] = value
        f.seek(0)
        json.dump(data, f, indent=4)
        f.truncate()


# set default config.json values
def set_default_values():
    update_json("language", "English, en")
    update_json("hearing_impaired", "Both")
    update_json("percentage_pass", 90)
    update_json("terminal_focus", "False")
    update_json("context_menu_icon", "True")
