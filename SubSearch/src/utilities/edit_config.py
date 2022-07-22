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


# set percentage threshold
def select_percentage_pass() -> None:
    ctypes.windll.kernel32.SetConsoleTitleW("SubSearch - Select percentage threshold")
    os.system("cls||clear")
    print(
        """
          The percentage threshold determines the amount of of words that need to
          match the subtitles found to be downloaded. If there are 10 words in the. 
          release name, 10%, means that only 1 word needs to match. Excluding, 
          quality e.g 720p.
          
          Subtitles for Tv-shows are usually not affected as much by this threshold,
          because if a season and episode match it gets automatically downloaded.
          Default value is 90, i.e 90% 
          
          """
    )
    while True:
        value = int(input("Enter number between 1-100: "))
        if value <= 100:
            break
        else:
            print("Must be a number between 1-100")
    update_json("percentage_pass", value)


# set if terminal is hidden or shown while searching
def select_terminal_focus() -> None:
    ctypes.windll.kernel32.SetConsoleTitleW("SubSearch - Select show Terminal while searching")
    os.system("cls||clear")
    print(
        """
          The terminal can be hidden or be shown while searching, hidden is default.
          If it's hidden and no subtitles are found, you can check the search.log,
          inside the the searched folder.
          
          """
    )
    while True:
        answer = input("Show terminal while searching? [y/N]: ")
        if answer.lower() == "y":
            value = "True"
            break
        if answer.lower() == "n" or len(answer) == 0:
            value = "False"
            break
        else:
            print("Please enter y or n")
    update_json("terminal_focus", value)


def select_hearing_impaired() -> None:
    ctypes.windll.kernel32.SetConsoleTitleW("SubSearch - Select hearing impaired subtitles")
    os.system("cls||clear")
    print(
        """
          Use hearing impaired subtitles?
          [y]es to only use HI
          [n]o to only use none-HI
          [b]oth to use both 
          
          """
    )
    while True:
        answer = input("Use hearing impared subtitles? [y/n/B]: ")
        if answer.lower() == "y":
            value = "True"
            break
        if answer.lower() == "n":
            value = "False"
            break
        if answer.lower() == "b" or len(answer) == 0:
            value = "Both"
            break
        else:
            print("Please enter y, n or b")
    update_json("hearing_impaired", value)


def select_cm_icon() -> None:
    ctypes.windll.kernel32.SetConsoleTitleW("SubSearch - Select show icon in context menu")
    os.system("cls||clear")
    print(
        """
          More or less just lets you turn the icon in the context menu on or off.
          Default is True, i.e on. 
          
          """
    )
    while True:
        answer = input("Icon in context menu [Y/n]: ")
        if answer.lower() == "y" or len(answer) == 0:
            value = "True"
            break
        if answer.lower() == "n":
            value = "False"
            break
        else:
            print("Please enter y or n")
    update_json("context_menu_icon", value)
