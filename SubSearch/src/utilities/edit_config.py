import json

from src.utilities.local_paths import root_directory


# update config.json
def update_json(key: str, value: str or int, directory: str = "data", file: str = "config.json"):
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
    update_json("context_menu_icon", "True")
    update_json("show_download_window", "False")
    update_json("terminal_focus", "False")
