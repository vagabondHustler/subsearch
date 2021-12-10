# setup_subscene
import ctypes
import sys
import os
import json

from src.os import root_directory_file
from src.current_user import is_admin
from src.regkey import write_key
from src.config import get


def context_menu() -> None:
    if is_admin():
        write_key()
        os.system(f'cmd /c "reg import regkey.reg"')
    else:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)


def update_language(language):
    with open(root_directory_file("config.json"), "r+", encoding="utf-8") as f:
        data = json.load(f)
        data["language"] = language
        f.seek(0)
        json.dump(data, f, indent=4)
        f.truncate()


def select_language():
    languages = get("languages")
    print("\n")
    print("[Fully supported languages]")
    for num, lang in enumerate(languages):
        if num < 10:
            print(f"{num}.  {lang}")
        else:
            print(f"{num}. {lang}")
    print("\n")
    print("[Supported languages] - Slower search times")
    print("Visit: https://u.subscene.com/filter")
    print("\n")
    while True:
        answer = int(input("Enter number for corresponding subtitle: "))
        for num, lang in enumerate(languages):
            if answer == num:
                update_language(lang)
                print("\n\n")
                break

        print("Not a valid number")
        print("Enter custom language from https://u.subscene.com/filter ?")
        choice = input("[y]/[N]: ")
        if choice.lower() == "y":
            print("Example: English")
            new_answer = input("Enter language: ")
            custom_answer = f"{new_answer}, en"
            update_language(custom_answer)
            print("\n\n")
            break
