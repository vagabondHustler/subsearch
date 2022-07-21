import webbrowser

import cloudscraper
from bs4 import BeautifulSoup
from src.data._version import current_version

SCRAPER = cloudscraper.create_scraper(
    browser={"browser": "chrome", "platform": "android", "desktop": False}
)


def check_for_updates(gui_running=False) -> bool:
    source = SCRAPER.get(
        "https://github.com/vagabondHustler/SubSearch/blob/main/SubSearch/src/data/_version.py"
    )
    scontent = source.content
    doc = BeautifulSoup(scontent, "lxml")
    doc_result = doc.find("span", class_="pl-s")

    latest_v = doc_result.text[1:-1]
    current_v = current_version()
    if gui_running:
        return current_v, latest_v
    else:
        if int(latest_v.replace(".", "")) > int(current_v.replace(".", "")):
            print("\nNew version available!")
            print(f"Your version: {current_v}, available version: {latest_v}")
            print("https://github.com/vagabondHustler/SubSearch/\n")
            go_to_github()
            return False
        print(f"Your version {current_v} is the latest version")
        print("Press enter to continue")
        return True


def go_to_github() -> None:
    while True:
        answer = input("Open link in webbrowser?: [Y/n] ")
        if answer.lower() == "y" or len(answer) == 0:
            webbrowser.open("https://github.com/vagabondHustler/SubSearch/releases")
            break
        if answer.lower() == "n":
            break
        else:
            print("Please enter y, n")
