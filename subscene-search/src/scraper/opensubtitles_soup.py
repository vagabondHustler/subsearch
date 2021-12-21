from bs4.element import ResultSet
import requests
from bs4 import BeautifulSoup

import time

# # check if subtitle is hearing impaired or not
# def is_sub_hi(a1: Tag) -> str:
#     a1_parent = a1.parent
#     a40 = a1_parent.find("td", class_="a40")  # non-hearing impaired
#     a41 = a1_parent.find("td", class_="a41")  # hearing impareded
#     if a40 is None:
#         return "False"
#     elif a41 is None:
#         return "True"

# search for title
def search_for_title(url: str) -> dict:
    titles: dict = {}
    source = requests.get(url)
    scontent = source.content
    doc = BeautifulSoup(scontent, "lxml")
    doc_results = doc.find("table", id="search_results")
    tr_name = doc_results.find_all("tr", id=lambda value: value and value.startswith("name"))
    for item in tr_name:
        print(item)
        tt = [a["title"] for a in item.find_all("a", title=True) if a.text]
        temptitle = tt[0]
        th = [a["href"] for a in item.find_all("a", href=True) if a.text]
        temphref = th[0]
        title = temptitle.strip().replace("subtitles - ", "")
        href = temphref.strip()
        link = f"https://www.opensubtitles.org{href}/sort-6/asc-0"
        titles[link] = title
    return titles


# search title(s) for subtitle
def search_title_for_sub(language_abbr: str, url: str) -> dict:
    subtitles: dict = {}
    source = requests.get(url)
    scontent = source.content
    doc = BeautifulSoup(scontent, "lxml")
    tbody = doc.find("tbody")
    onclick = tbody.find_all("tr", onclick=True)
    for item in onclick:
        rn1 = item.get_text().split(")")
        rs2 = rn1[-1].split("Watch")
        release_name = rs2[0].lower()
        data = item.find("a", class_="bnone")
        link = f'https://www.opensubtitles.org{data["href"]}'
        # title = data["title"].replace("subtitles - ", "")
        if link.endswith(language_abbr):
            subtitles[link] = release_name
    return subtitles


# get download url for subtitle(s)
def get_download_url(url: str) -> str:
    source = requests.get(url).text
    doc = BeautifulSoup(source, "lxml")
    _link = [dl["href"] for dl in doc.find_all("a", href=True, id="bt-dwl-bt")]
    download_url = f"https://www.opensubtitles.org{_link[0]}"
    return download_url
