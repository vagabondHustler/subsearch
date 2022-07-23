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


def set_default_values():
    update_json("language", "English, en")
    update_json("hearing_impaired", "Both")
    update_json("percentage_pass", 90)
    update_json("terminal_focus", "False")
    update_json("context_menu_icon", "True")


# set language
def select_language() -> None:
    ctypes.windll.kernel32.SetConsoleTitleW("SubSearch - Select language")
    os.system("cls||clear")
    languages = get("languages")
    print("[Fully supported languages]")
    for num, value in enumerate(languages):
        if num < 10:
            print(f"{num}.  {value}")
        else:
            print(f"{num}. {value}")
    print("\n")
    print("[Supported languages]")
    print("Visit: https://u.subscene.com/filter")
    print("\n")
    while True:
        answer = int(input("Enter number for corresponding subtitle: "))
        for num, value in enumerate(languages):
            if answer == num:
                update_json("language", value)
                return
            elif answer != num and num >= len(languages):
                print("Not a valid number")
                print("Enter custom language from https://u.subscene.com/filter ?")
                choice = input("[y]/[N]: ")
                if choice.lower() == "y":
                    print("Example: English")
                    new_answer = input("Enter language: ")
                    custom_answer = f"{new_answer}, en"
                    update_json("language", custom_answer)
                    return
