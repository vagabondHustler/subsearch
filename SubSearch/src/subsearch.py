import ctypes
import time

from src.data._version import current_version
from src.local_paths import cwd
from src.scraper import opensubtitles, subscene
from src.utilities import edit_config, edit_registry
from src.utilities import file_manager as ufm
from src.utilities import log
from src.utilities.current_user import got_key
from src.utilities.fetch_config import get
from src.utilities.fetch_data import get_parameters


def main() -> None:
    # initialising
    start = time.perf_counter()
    version = current_version()
    ctypes.windll.kernel32.SetConsoleTitleW(f"SubSearch - v{version}")
    if got_key() is False:
        edit_config.set_default_values()
        edit_registry.add_context_menu()
        return

    language, lang_abbr = get("language")
    hearing_impaired = get("hearing_impaired")
    precentage = get("percentage")
    focus = get("terminal_focus")
    video_ext: list = get("video_ext")
    video = ufm.find_video(cwd(), video_ext, False)
    video_with_ext = ufm.find_video(cwd(), video_ext, True)
    if video_with_ext is not None:
        file_hash = ufm.get_hash(video_with_ext)
    elif video_with_ext is None:
        file_hash = None

    # TODO fix this so no try is needed
    try:
        param = get_parameters(cwd().lower(), lang_abbr, file_hash, video)
    except IndexError as err:
        log.output(err)
        if focus == "True":
            return input()
        return

    # log parameters
    log.parameters(param, language, lang_abbr, hearing_impaired, precentage)

    # scrape with parameters
    log.output("")
    log.output("[Searching opensubtitles]")
    scrape_os = opensubtitles.scrape(param, language, hearing_impaired) if file_hash is not None else None
    log.output("")
    log.output("[Searching subscene]")
    scrape_ss = subscene.scrape(param, language, lang_abbr, hearing_impaired, precentage)
    if scrape_os is None and scrape_ss is None:
        elapsed = time.perf_counter() - start
        log.output(f"Finished in {elapsed} seconds.")
        if focus == "True":
            return input()
        return

    # download files from scrape results
    if scrape_os is not None:
        log.output("")
        log.output("[Downloading from Opensubtitles]")
        for item in scrape_os:
            ufm.download_zip(item)
    if scrape_ss is not None:
        log.output("")
        log.output("[Downloading from Subscene]")
        for item in scrape_ss:
            ufm.download_zip(item)

    # procsess downloaded files
    log.output("")
    log.output("[Procsessing files]")
    ufm.extract_zips(cwd(), ".zip")
    ufm.clean_up(cwd(), ".zip")
    ufm.clean_up(cwd(), ").nfo")
    ufm.rename_srts(f"{param.release}.srt", cwd(), f"{param.group}.srt", ".srt")
    ufm.move_files(cwd(), f"{param.release}.srt", ".srt")
    log.output("")

    # finnishing up
    elapsed = time.perf_counter() - start
    log.output(f"Finished in {elapsed} seconds")

    if focus == "True":
        input()
