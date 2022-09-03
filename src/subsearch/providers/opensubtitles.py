import re
from typing import Union

from subsearch.data import __video__
from subsearch.providers import generic
from subsearch.providers.generic import BaseChecks, BaseProvider, DownloadData
from subsearch.utils import log, string_parser
from subsearch.utils.raw_config import UserParameters
from subsearch.utils.string_parser import FileSearchParameters


class OpenSubtitles(BaseProvider):
    def __init__(self, parameters: FileSearchParameters, user_parameters: UserParameters):
        BaseProvider.__init__(self, parameters, user_parameters)
        self.scrape = OpenSubtitlesScrape()
        self.check = BaseChecks()

    def parse_hash(self):
        to_be_downloaded: list[str] | None = self.scrape.hash(self.url_hash, self.current_language, self.hearing_impaired)
        if to_be_downloaded is None and self.series:
            log.output(f"No TV-series found matching hash {self.file_hash}")
            log.output(f"Done with tasks\n")
            return None
        if to_be_downloaded is None:
            log.output(f"No movies found matching hash {self.file_hash}")
            log.output(f"Done with tasks\n")
            return None

        download_info = []
        log.output(f"Preparing  hash {self.file_hash} for download")
        tbd_lenght = len(to_be_downloaded)
        for zip_idx, zip_url in enumerate(to_be_downloaded, start=1):
            zip_fp = f"{__video__.directory}\\__subsearch__opensubtitles_{zip_idx}.zip"
            data = DownloadData(file_path=zip_fp, url=zip_url, idx_num=zip_idx, idx_lenght=tbd_lenght)
            download_info.append(data)
        log.output(f"Done with tasks\n")
        return download_info

    def parse_rss(self):
        to_be_sorted = []
        results = self.scrape.rss_subtitles(self.url_opensubtitles)
        to_be_downloaded: dict[str, str] = {}
        to_be_sorted: list[tuple[int, str, str]] = []
        for key, value in results.items():
            number = string_parser.get_pct_value(key, self.release)
            log.output(f"[Found]: {key}")
            lenght_str = sum(1 for char in f"[{number}% match]:")
            formatting_spaces = " " * lenght_str
            _name = f"[{number}% match]: {key}"
            _url = f"{formatting_spaces} {value}"
            to_be_sorted_value = number, _name, _url
            to_be_sorted.append(to_be_sorted_value)
            if self.check.is_threshold_met(key, self.title, self.season, self.episode, self.series, number, self.pct):
                to_be_downloaded[key] = value if key not in to_be_downloaded else None
        self._sorted_list = generic.log_and_sort_list("opensubtitles", to_be_sorted, self.pct)
        # exit if no subtitles found
        if len(to_be_downloaded) == 0:
            log.output(f"No subtitles to download for {self.release}")
            log.output("Done with tasks\n")
            return None

        download_info = []
        tbd_lenght = len(to_be_downloaded)
        for zip_idx, (zip_name, zip_url) in enumerate(to_be_downloaded.items(), start=1):
            zip_fp = f"{__video__.directory}\\__subsearch__opensubtitles_{zip_idx}.zip"
            data = DownloadData(name=zip_name, file_path=zip_fp, url=zip_url, idx_num=zip_idx, idx_lenght=tbd_lenght)
            download_info.append(data)
        log.output("Done with tasks\n")
        return download_info

    def sorted_list(self):
        return self._sorted_list


class OpenSubtitlesScrape:
    def __init__(self):
        self.check = BaseChecks()

    def rss_subtitles(self, url: str):
        subtitles: dict[str, str] = {}
        doc = generic.get_lxml_doc(url, "xml")
        items = doc.find_all("item")
        for item in items:
            dl_url = item.enclosure["url"]
            released_as = item.description.text.strip()
            release_name = re.findall("^.*?: (.*?);", released_as)[0]  # https://regex101.com/r/LWAmJK/1
            subtitles[release_name] = dl_url
        return subtitles

    def hash(self, url: str, current_language: str, hearing_impaired: Union[str, bool]) -> list[str] | None:
        download_url: list[str] = []
        doc = generic.get_lxml_doc(url, "lxml")
        doc_results = doc.find("table", id="search_results")
        if doc_results is None:
            return None
        tr_name = doc_results.find_all("tr", id=lambda value: value and value.startswith("name"))
        for item in tr_name:
            tl = [a["title"] for a in item.find_all("a", title=current_language)]
            if current_language not in tl:
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
