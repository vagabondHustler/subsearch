import requests
from bs4 import BeautifulSoup
import time


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


def search_title_for_sub(language: str, url: str) -> dict:
    searching = True
    subtitles: dict = {}
    while searching:
        source = requests.get(url)
        scontent = source.content
        doc = BeautifulSoup(scontent, "lxml")
        tbody = doc.find("tbody")
        if tbody is not None:
            tbc = tbody.find_all("td", class_="a1")
            searching = False
        else:
            time.sleep(1)

    for i in tbc:
        if language == i.span.get_text().strip():
            _release_name = [x.get_text().strip() for x in i.find("a")]
            release_name = _release_name[-2]
            link = [y["href"] for y in i.find_all("a", href=True) if y.text]
            subtitles[release_name] = f"https://subscene.com/{link[0]}"
    return subtitles


def get_download_url(url: str) -> str:
    source = requests.get(url).text
    doc = BeautifulSoup(source, "lxml")
    _link = [dl["href"] for dl in doc.find_all("a", href=True, id="downloadButton")]
    download_url = f"https://subscene.com/{_link[0]}"
    return download_url
