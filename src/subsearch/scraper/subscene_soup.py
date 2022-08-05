import time

import cloudscraper
from bs4 import BeautifulSoup
from bs4.element import Tag

SCRAPER = cloudscraper.create_scraper(browser={"browser": "chrome", "platform": "android", "desktop": False})

# check if subtitle is hearing impaired or not
def is_sub_hi(a1: Tag) -> str:
    a1_parent = a1.parent
    a40 = a1_parent.find("td", class_="a40")  # non-hearing impaired
    a41 = a1_parent.find("td", class_="a41")  # hearing imparted
    if a40 is None:
        return "True"
    elif a41 is None:
        return "False"


# search for title
def search_for_title(url: str) -> dict | str:
    titles: dict = {}
    source = SCRAPER.get(url)
    scontent = source.content
    doc = BeautifulSoup(scontent, "lxml")
    doc_result = doc.find("div", class_="search-result")
    if doc_result is None:
        doc_captcha = doc.find("h2", text="Why do I have to complete a CAPTCHA?")
        if doc_captcha.text == "Why do I have to complete a CAPTCHA?":
            return "ERROR: CAPTCHA PROTECTION"
    results = doc_result.find_all("div", class_="title")
    for i in results:
        get_title = i.get_text().strip().replace("'", "").replace(":", "").lower()
        link = [a["href"] for a in i.find_all("a", href=True) if a.text]
        titles[get_title] = f"https://subscene.com/{link[0]}"
    return titles


# search title(s) for subtitle
def search_title_for_sub(language: str, hearing_impaired: str, url: str) -> dict:
    searching = True
    subtitles: dict = {}
    while searching:
        source = SCRAPER.get(url)
        scontent = source.content
        doc = BeautifulSoup(scontent, "lxml")
        tbody = doc.find("tbody")
        if tbody is not None:
            tda1 = tbody.find_all("td", class_="a1")
            searching = False
        else:
            time.sleep(1)

    for a1 in tda1:
        sub_hi = is_sub_hi(a1)
        if hearing_impaired != "Both" and hearing_impaired != sub_hi:
            continue
        if language == a1.span.get_text().strip():
            _release_name = [x.get_text().strip() for x in a1.find("a")]
            release_name = _release_name[-2]
            if " " in release_name:
                release_name = release_name.replace(" ", ".")
            link = [y["href"] for y in a1.find_all("a", href=True) if y.text]
            subtitles[release_name] = f"https://subscene.com/{link[0]}"

    return subtitles


# get download url for subtitle(s)
def get_download_url(url: str) -> dict:
    source = SCRAPER.get(url).text
    doc = BeautifulSoup(source, "lxml")
    _link = [dl["href"] for dl in doc.find_all("a", href=True, id="downloadButton")]
    download_url = f"https://subscene.com/{_link[0]}"
    return download_url
