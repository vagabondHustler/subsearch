from typing import NamedTuple, Union

import requests
from bs4 import BeautifulSoup

from subsearch.data import __video_directory__
from subsearch.utils import log
from subsearch.utils.raw_config import UserParameters
from subsearch.utils.string_parser import FileSearchParameters


def get_lxml_doc(url: str) -> BeautifulSoup:
    source = requests.get(url)
    scontent = source.content
    doc = BeautifulSoup(scontent, "lxml")
    return doc


class OpenSubtitlesData(NamedTuple):
    file_path: str
    url: str
    idx_num: int
    idx_lenght: int


class OpenSubtitles:
    def __init__(self, parameters: FileSearchParameters, user_parameters: UserParameters):
        # file parameters
        self.url_opensubtitles = parameters.url_opensubtitles
        self.title = parameters.title
        self.year = parameters.year
        self.season = parameters.season
        self.season_ordinal = parameters.season_ordinal
        self.episode = parameters.episode
        self.episode_ordinal = parameters.episode_ordinal
        self.show_bool = parameters.show_bool
        self.release = parameters.release
        self.group = parameters
        self.file_hash = parameters.file_hash
        # user parameters
        self.language = user_parameters.language
        self.lang_code2 = user_parameters.lang_code2
        self.hearing_impaired = user_parameters.hearing_impaired
        self.pct = user_parameters.pct
        self.show_download_window = user_parameters.show_dl_window
        # scraper
        self.scrape = OpenSubtitlesScrape()
        # checks
        self.check = OpenSubtitlesChecks()

    def parse_hash(self):
        to_be_downloaded: list[str] | None = self.scrape.search_for_hash(
            self.url_opensubtitles, self.language, self.hearing_impaired
        )
        if to_be_downloaded is None:
            if self.show_bool:
                log.output(f"No TV-series found matching hash {self.file_hash}")
            log.output(f"No movies found matching hash {self.file_hash}")
            return None
        else:
            download_info = []
            log.output(f"Preparing  hash {self.file_hash} for download")
            tbd_lenght = len(to_be_downloaded)
            for zip_idx, zip_url in enumerate(to_be_downloaded, start=1):
                zip_fp = f"{__video_directory__}\\__subsearch__opensubtitles_{zip_idx}.zip"
                data = OpenSubtitlesData(file_path=zip_fp, url=zip_url, idx_num=zip_idx, idx_lenght=tbd_lenght)
                download_info.append(data)
            log.output(f"Done with tasks")
            return download_info


class OpenSubtitlesScrape:
    def __init__(self):
        self.check = OpenSubtitlesChecks()

    def search_for_hash(self, url: str, language: str, hearing_impaired: Union[str, bool]) -> list[str] | None:
        download_url: list[str] = []
        doc = get_lxml_doc(url)
        doc_results = doc.find("table", id="search_results")
        if doc_results is None:
            return None
        tr_name = doc_results.find_all("tr", id=lambda value: value and value.startswith("name"))
        for item in tr_name:
            tl = [a["title"] for a in item.find_all("a", title=language)]
            if language not in tl:
                continue
            hi_site = item.find("img", alt="Subtitles for hearing impaired")
            if hi_site is not None and hearing_impaired is False:
                log.output(f"Found HI-subtitle but skipping, 'cus hearing impaired is set to '{hearing_impaired}'")
                continue
            if hi_site is None and hearing_impaired is True:
                log.output(f"Found nonHI-subtitle but skipping, 'cus hearing impaired is set to '{hearing_impaired}'")
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


class OpenSubtitlesChecks:
    def __init__(self) -> None:
        pass
