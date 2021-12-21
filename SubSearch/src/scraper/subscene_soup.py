from bs4.element import Tag
import requests
from bs4 import BeautifulSoup
import time

# check if subtitle is hearing impaired or not
def is_sub_hi(a1: Tag) -> str:
    a1_parent = a1.parent
    a40 = a1_parent.find("td", class_="a40")  # non-hearing impaired
    a41 = a1_parent.find("td", class_="a41")  # hearing impareded
    if a40 is None:
        return "True"
    elif a41 is None:
        return "False"


# search for title
def search_for_title(url: str) -> dict:
    titles: dict = {}
    source = requests.get(url)
    scontent = source.content
    doc = BeautifulSoup(scontent, "lxml")
    doc_result = doc.find("div", class_="search-result")
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
        source = requests.get(url)
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
            link = [y["href"] for y in a1.find_all("a", href=True) if y.text]
            subtitles[release_name] = f"https://subscene.com/{link[0]}"
    return subtitles


# get download url for subtitle(s)
def get_download_url(url: str) -> str:
    source = requests.get(url).text
    doc = BeautifulSoup(source, "lxml")
    _link = [dl["href"] for dl in doc.find_all("a", href=True, id="downloadButton")]
    download_url = f"https://subscene.com/{_link[0]}"
    return download_url
