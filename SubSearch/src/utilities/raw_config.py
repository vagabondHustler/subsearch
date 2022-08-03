import json

from src.utilities import local_paths

# update config.json
def set_json(key: str, value: str or int, directory: str = "data", file: str = "config.json"):
    with open(local_paths.get_path(directory, file), "r+", encoding="utf-8") as f:
        data = json.load(f)
        data[key] = value
        f.seek(0)
        json.dump(data, f, indent=4)
        f.truncate()


def get_json():
    config_file = local_paths.get_path("data", "config.json")
    with open(config_file, encoding="utf-8") as file:
        data = json.load(file)

    return data


# get said value(s) from config.json
def get(output: str):
    config_json_dict = {
        "language": get_json()["language"].split(", "),
        "languages": get_json()["languages"],
        "other_languages": get_json()["other_languages"],
        "hearing_impaired": get_json()["hearing_impaired"],
        "percentage": get_json()["percentage_pass"],
        "cm_icon": get_json()["context_menu_icon"],
        "show_download_window": get_json()["show_download_window"],
        "show_terminal": get_json()["show_terminal"],
        "video_ext": get_json()["video_ext"],
    }
    return config_json_dict[f"{output}"]


# set default config.json values
def set_default_json():
    set_json("language", "English, en")
    set_json("hearing_impaired", "Both")
    set_json("percentage_pass", 90)
    set_json("context_menu_icon", "True")
    set_json("show_download_window", "True")
    set_json("show_terminal", "False")
