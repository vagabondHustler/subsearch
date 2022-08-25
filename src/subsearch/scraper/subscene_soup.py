import time
from typing import Literal, Optional, Union

import cloudscraper
from bs4 import BeautifulSoup
from bs4.element import Tag

SCRAPER = cloudscraper.create_scraper(browser={"browser": "chrome", "platform": "android", "desktop": False})


def is_sub_hi(a1: Tag) -> Optional[bool]:
    a1_parent = a1.parent
    a40 = a1_parent.find("td", class_="a40")  # non-hearing impaired
    a41 = a1_parent.find("td", class_="a41")  # hearing imparted
    if a40 is None:
        return True
    elif a41 is None:
        return False

    return None


def search_for_title(url: str) -> (Union[dict[str, str], Literal["ERROR: CAPTCHA PROTECTION"]]):
    titles: dict[str, str] = {}
    source = SCRAPER.get(url)
    scontent = source.content
    doc = BeautifulSoup(scontent, "lxml")
    doc_result = doc.find("div", class_="search-result")
    if doc_result is None:
        doc_captcha = doc.find("h2", text="Why do I have to complete a CAPTCHA?")
        if doc_captcha.text == "Why do I have to complete a CAPTCHA?":
            return "ERROR: CAPTCHA PROTECTION"
    div_title = doc_result.find_all("div", class_="title")
    for item in div_title:
        title_name = item.contents[1].contents[0].strip().replace(":", "")
        title_url = item.contents[1].attrs["href"]
        titles[title_name] = f"https://subscene.com{title_url}"
    return titles


def search_title_for_sub(language: str, hearing_impaired: Union[bool, str], url: str) -> dict[str, str]:
    searching = True
    subtitles: dict[str, str] = {}
    while searching:
        source = SCRAPER.get(url)
        scontent = source.content
        doc = BeautifulSoup(scontent, "lxml")
        tbody = doc.find("tbody")
        if tbody is not None:
            td_a1 = tbody.find_all("td", class_="a1")
            searching = False
        else:
            time.sleep(1)
    for a1 in td_a1:
        sub_hi = is_sub_hi(a1)
        subtitle_language = a1.contents[1].contents[1].contents[0].strip()
        if hearing_impaired != "Both" and hearing_impaired != sub_hi:
            continue
        if language == subtitle_language:
            release_name = a1.contents[1].contents[3].string.strip()
            if " " in release_name:
                release_name = release_name.replace(" ", ".")
            subtitle_url = a1.contents[1].attrs["href"]
            subtitles[release_name] = f"https://subscene.com{subtitle_url}"

    return subtitles


def get_download_url(url: str) -> str:
    source = SCRAPER.get(url).text
    doc = BeautifulSoup(source, "lxml")
    button_url = [dl["href"] for dl in doc.find_all("a", href=True, id="downloadButton")]
    download_url = f"https://subscene.com/{button_url[0]}"
    return download_url
