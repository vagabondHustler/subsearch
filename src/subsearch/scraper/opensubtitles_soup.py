from typing import Optional, Union

import requests
from bs4 import BeautifulSoup

from subsearch.utils import log


# search for file hash
def search_for_hash(url: str, lang: str, hi: Union[str, bool]) -> Optional[list[str]]:
    download_url: list[str] = []
    source = requests.get(url)
    scontent = source.content
    doc = BeautifulSoup(scontent, "lxml")
    doc_results = doc.find("table", id="search_results")
    if doc_results is None:
        return None
    tr_name = doc_results.find_all("tr", id=lambda value: value and value.startswith("name"))
    for item in tr_name:
        tl = [a["title"] for a in item.find_all("a", title=lang)]
        if lang in tl:
            hi_site = item.find("img", alt="Subtitles for hearing impaired")
            if hi_site is not None and hi is False:
                log.output(f"Found HI-subtitle but skipping, 'cus hearing impaired is set to '{hi}'")
                continue
            if hi_site is None and hi is True:
                log.output(f"Found nonHI-subtitle but skipping, 'cus hearing impaired is set to '{hi}'")
                continue

            title_name = item.find("a", class_="bnone").text.replace("\n", "").replace("\t", "").replace("(", " (")
            log.output(f"{title_name} matched file hash")
            th = [
                a["href"]
                for a in item.find_all(
                    "a",
                    href=lambda value: value and value.startswith("/en/subtitleserve/sub/"),
                )
            ]
            th = th[0] if th is not None else None
            link = f"https://www.opensubtitles.org{th}"
            download_url.append(link) if th is not None else None
    if len(download_url) == 0:
        return None
    return download_url
