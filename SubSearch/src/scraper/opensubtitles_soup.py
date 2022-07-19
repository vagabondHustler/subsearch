import requests
from bs4 import BeautifulSoup
from src.utilities import log


# search for file hash
def search_for_hash(url: str, language: str, hearing_impaired: str) -> list or None:
    download_url: list = []
    source = requests.get(url)
    scontent = source.content
    doc = BeautifulSoup(scontent, "lxml")
    doc_results = doc.find("table", id="search_results")
    if doc_results is None:
        return None
    tr_name = doc_results.find_all("tr", id=lambda value: value and value.startswith("name"))
    for item in tr_name:
        tl = [a["title"] for a in item.find_all("a", title=language)]
        if language in tl:
            hi = item.find("img", alt="Subtitles for hearing impaired")
            if hi is not None and hearing_impaired == "False":
                log.output(
                    f"Found HI-subtitle but skipping, 'cus hearing impaired is set to '{hearing_impaired}'"
                )
                continue
            if hi is None and hearing_impaired == "True":
                log.output(
                    f"Found nonHI-subtitle but skipping, 'cus hearing impaired is set to '{hearing_impaired}'"
                )
                continue

            title_name = (
                item.find("a", class_="bnone")
                .text.replace("\n", "")
                .replace("\t", "")
                .replace("(", " (")
            )
            log.output(f"{title_name} matched file hash")
            th = [
                a["href"]
                for a in item.find_all(
                    "a", href=lambda value: value and value.startswith("/en/subtitleserve/sub/")
                )
            ]
            th = th[0] if th is not None else None
            link = f"https://www.opensubtitles.org{th}"
            download_url.append(link) if th is not None else None
    if len(download_url) == 0:
        return None
    return download_url
